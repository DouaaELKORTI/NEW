from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from autogluon.tabular import TabularPredictor
import pandas as pd
import json, os
from pathlib import Path
from datetime import datetime

# =============================
# Paths
# =============================
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "autogluon_health_model"
DATA_PATH = BASE_DIR / "data" / "sensors_without_health.json"
HISTORY_PATH = BASE_DIR / "data" / "realtime_health_history.json"

# =============================
# App
# =============================
app = FastAPI(title="Blood Bag Real-Time Monitoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================
# Load model
# =============================
predictor = TabularPredictor.load(
    str(MODEL_PATH),
    require_version_match=False,
    require_py_version_match=False
)

# =============================
# Load dataset
# =============================
raw = pd.read_json(DATA_PATH)
raw["timestamp"] = pd.to_datetime(raw["timestamp"])
raw = raw.sort_values(["bag_id", "timestamp"]).reset_index(drop=True)

BAG_IDS = sorted(raw["bag_id"].unique().tolist())

# Group by bag
bag_records = {bid: df.reset_index(drop=True) for bid, df in raw.groupby("bag_id")}

# Runtime state
state = {
    "idx": {bid: 0 for bid in BAG_IDS},
    "last_health": {bid: 1.0 for bid in BAG_IDS},
    "start_time": {bid: None for bid in BAG_IDS},
    "cum": {
        bid: {
            "door": 0,
            "accel": 0.0,
            "handling": 0.0,
            "light": 0.0,
            "frac6": 0.0,
            "frac8": 0.0,
            "temp_dev6": 0.0,
        }
        for bid in BAG_IDS
    }
}

# Load history if exists
if HISTORY_PATH.exists():
    try:
        history = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        # restore last health from history
        for rec in history:
            bid = rec["bag_id"]
            state["last_health"][bid] = min(state["last_health"].get(bid, 1.0), rec["predicted_health_index"])
    except Exception:
        history = []
else:
    history = []

def status_label(hi: float) -> str:
    if hi >= 0.85:
        return "SAFE"
    if hi >= 0.65:
        return "WARNING"
    return "UNSAFE"

def build_features(row: dict, bid: str) -> pd.DataFrame:
    """
    Rebuild features similar to training pipeline.
    Uses cumulative features maintained in memory.
    """
    now = pd.Timestamp.now()

    # init start time per bag
    if state["start_time"][bid] is None:
        state["start_time"][bid] = now

    elapsed_hours = (now - state["start_time"][bid]).total_seconds() / 3600.0

    # update cumulative
    c = state["cum"][bid]
    c["door"] += int(row["door_count"])
    c["accel"] += float(row["accel_rms"])
    c["handling"] += float(row["handling_stress"])
    c["light"] += float(row["light_mean_abs"])
    c["frac6"] += float(row["frac_temp_above_6"])
    c["frac8"] += float(row["frac_temp_above_8"])

    temp_dev_above_6 = max(float(row["temp_mean"]) - 6.0, 0.0)
    c["temp_dev6"] += temp_dev_above_6

    df = pd.DataFrame([{
        # raw sensors
        "temp_mean": float(row["temp_mean"]),
        "temp_min": float(row["temp_min"]),
        "temp_max": float(row["temp_max"]),
        "temp_std": float(row["temp_std"]),
        "frac_temp_above_6": float(row["frac_temp_above_6"]),
        "frac_temp_above_8": float(row["frac_temp_above_8"]),
        "hum_mean": float(row["hum_mean"]),
        "hum_std": float(row["hum_std"]),
        "accel_rms": float(row["accel_rms"]),
        "door_count": int(row["door_count"]),
        "light_mean_abs": float(row["light_mean_abs"]),
        "handling_stress": float(row["handling_stress"]),
        "route": str(row["route"]),
        "blood_type": str(row["blood_type"]),

        # time features
        "timestamp": now,
        "elapsed_hours": float(elapsed_hours),
        "hour_of_day": int(now.hour),
        "day_of_week": int(now.dayofweek),

        # cumulative features
        "cum_door_count": int(c["door"]),
        "cum_accel_rms": float(c["accel"]),
        "cum_handling_stress": float(c["handling"]),
        "cum_light_mean_abs": float(c["light"]),
        "cum_frac_temp_above_6": float(c["frac6"]),
        "cum_frac_temp_above_8": float(c["frac8"]),
        "temp_dev_above_6": float(temp_dev_above_6),
        "cum_temp_dev_above_6": float(c["temp_dev6"]),
    }])

    # one-hot encode
    df = pd.get_dummies(df, columns=["route", "blood_type"], drop_first=False)

    expected_cols = [
        "route_Hospital_1", "route_Hospital_2", "route_Hospital_3", "route_Hospital_4",
        "blood_type_A+", "blood_type_A-", "blood_type_AB+", "blood_type_AB-",
        "blood_type_B+", "blood_type_B-", "blood_type_O+", "blood_type_O-",
    ]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0

    return df

def predict_one(bid: str) -> dict:
    df_bag = bag_records[bid]
    i = state["idx"][bid]

    # loop when end reached
    if i >= len(df_bag):
        i = 0
        state["idx"][bid] = 0
        state["start_time"][bid] = None
        state["cum"][bid] = {
            "door": 0, "accel": 0.0, "handling": 0.0, "light": 0.0,
            "frac6": 0.0, "frac8": 0.0, "temp_dev6": 0.0
        }

    row = df_bag.iloc[i].to_dict()
    state["idx"][bid] += 1

    X = build_features(row, bid)
    pred = float(predictor.predict(X).iloc[0])

    # monotonic degradation
    pred = min(pred, state["last_health"].get(bid, pred))
    pred = max(min(pred, 1.0), 0.0)
    state["last_health"][bid] = pred

    payload = {
        "bag_id": bid,
        "timestamp": datetime.now().isoformat(),
        "dataset_timestamp": str(row["timestamp"]),
        "blood_type": row["blood_type"],
        "route": row["route"],
        "predicted_health_index": pred,
        "status": status_label(pred),

        # show key indicators
        "temp_mean": row["temp_mean"],
        "hum_mean": row["hum_mean"],
        "accel_rms": row["accel_rms"],
        "door_count": row["door_count"],
        "light_mean_abs": row["light_mean_abs"],
        "handling_stress": row["handling_stress"],
    }

    history.append(payload)
    HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")

    return payload

@app.get("/health")
def health():
    return {"ok": True, "bags": len(BAG_IDS)}

@app.get("/bags")
def list_bags():
    return {"bags": BAG_IDS}

@app.get("/snapshot")
def snapshot():
    """
    This is your "real monitoring tick".
    Each call advances one record per bag and returns the full monitoring view.
    """
    results = [predict_one(bid) for bid in BAG_IDS]
    return {
        "server_time": datetime.now().isoformat(),
        "interval_seconds": 15,
        "bags": results
    }

@app.get("/history/{bag_id}")
def get_history(bag_id: str):
    bag_hist = [r for r in history if r["bag_id"] == bag_id]
    return {"bag_id": bag_id, "records": bag_hist[-500:]}  # keep last 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
