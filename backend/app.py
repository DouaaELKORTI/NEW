from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from autogluon.tabular import TabularPredictor
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "autogluon_health_model"
DATA_PATH = BASE_DIR / "data" / "sensors_without_health.json"
HISTORY_PATH = BASE_DIR / "data" / "realtime_health_history.json"

TEMP_MIN = 2.0
TEMP_MAX = 6.0
INTERVAL_SECONDS = 15
DAMAGE_SCALE = 0.15

app = FastAPI(title="Blood Bag Monitoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = TabularPredictor.load(
    str(MODEL_PATH),
    require_version_match=False,
    require_py_version_match=False,
)

raw = pd.read_json(DATA_PATH)
raw["timestamp"] = pd.to_datetime(raw["timestamp"])
raw = raw.sort_values(["bag_id", "timestamp"]).reset_index(drop=True)

BAG_IDS = sorted(raw["bag_id"].unique().tolist())
bag_records = {bid: df.reset_index(drop=True) for bid, df in raw.groupby("bag_id")}

INITIAL_HEALTH = {bid: 1.0 for bid in BAG_IDS}
INITIAL_HEALTH["BAG_0009"] = 0.72
INITIAL_HEALTH["BAG_0010"] = 0.55

state = {
    "idx": {bid: 0 for bid in BAG_IDS},
    "last_health": {bid: INITIAL_HEALTH[bid] for bid in BAG_IDS},
    "start_time": {bid: None for bid in BAG_IDS},
    "temp_out_seconds": {bid: 0 for bid in BAG_IDS},
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
    },
}

history = []
if HISTORY_PATH.exists():
    try:
        history = json.loads(HISTORY_PATH.read_text())
        for r in history:
            bid = r["bag_id"]
            state["last_health"][bid] = min(
                state["last_health"][bid],
                r["predicted_health_index"],
            )
    except Exception:
        history = []

def status_label(hi: float) -> str:
    if hi >= 0.85:
        return "SAFE"
    if hi >= 0.65:
        return "WARNING"
    return "UNSAFE"

def build_features(row: dict, bid: str) -> pd.DataFrame:
    now = pd.Timestamp.now()

    if state["start_time"][bid] is None:
        state["start_time"][bid] = now

    elapsed_hours = (now - state["start_time"][bid]).total_seconds() / 3600.0

    c = state["cum"][bid]
    c["door"] += int(row["door_count"])
    c["accel"] += float(row["accel_rms"])
    c["handling"] += float(row["handling_stress"])
    c["light"] += float(row["light_mean_abs"])
    c["frac6"] += float(row["frac_temp_above_6"])
    c["frac8"] += float(row["frac_temp_above_8"])

    temp_dev = max(row["temp_mean"] - 6.0, 0.0)
    c["temp_dev6"] += temp_dev

    df = pd.DataFrame([{
        "temp_mean": row["temp_mean"],
        "temp_min": row["temp_min"],
        "temp_max": row["temp_max"],
        "temp_std": row["temp_std"],
        "frac_temp_above_6": row["frac_temp_above_6"],
        "frac_temp_above_8": row["frac_temp_above_8"],
        "hum_mean": row["hum_mean"],
        "hum_std": row["hum_std"],
        "accel_rms": row["accel_rms"],
        "door_count": row["door_count"],
        "light_mean_abs": row["light_mean_abs"],
        "handling_stress": row["handling_stress"],
        "route": row["route"],
        "blood_type": row["blood_type"],
        "elapsed_hours": elapsed_hours,
        "hour_of_day": now.hour,
        "day_of_week": now.dayofweek,
        "cum_door_count": c["door"],
        "cum_accel_rms": c["accel"],
        "cum_handling_stress": c["handling"],
        "cum_light_mean_abs": c["light"],
        "cum_frac_temp_above_6": c["frac6"],
        "cum_frac_temp_above_8": c["frac8"],
        "temp_dev_above_6": temp_dev,
        "cum_temp_dev_above_6": c["temp_dev6"],
    }])

    df = pd.get_dummies(df, columns=["route", "blood_type"], drop_first=False)

    expected = [
        "route_Hospital_1", "route_Hospital_2", "route_Hospital_3", "route_Hospital_4",
        "blood_type_A+", "blood_type_A-", "blood_type_AB+", "blood_type_AB-",
        "blood_type_B+", "blood_type_B-", "blood_type_O+", "blood_type_O-",
    ]
    for col in expected:
        if col not in df.columns:
            df[col] = 0

    return df

def apply_remaining_quality(bid: str, model_raw: float):
    prev = state["last_health"][bid]
    model_raw = max(min(model_raw, 1.0), 0.0)
    damage = (1.0 - model_raw) * DAMAGE_SCALE
    new_health = max(min(prev - damage, prev), 0.0)
    state["last_health"][bid] = new_health
    return new_health

def predict_one(bid: str):
    df_bag = bag_records[bid]
    i = state["idx"][bid]

    if i >= len(df_bag):
        state["idx"][bid] = 0
        state["start_time"][bid] = None
        state["temp_out_seconds"][bid] = 0
        i = 0

    row = df_bag.iloc[i].to_dict()
    state["idx"][bid] += 1

    temp = row["temp_mean"]
    if temp < TEMP_MIN or temp > TEMP_MAX:
        state["temp_out_seconds"][bid] += INTERVAL_SECONDS
    else:
        state["temp_out_seconds"][bid] = 0

    X = build_features(row, bid)
    model_raw = float(predictor.predict(X).iloc[0])
    hi = apply_remaining_quality(bid, model_raw)
    status = status_label(hi)

    minutes_out = state["temp_out_seconds"][bid] // 60
    reason = None

    if status == "WARNING" and minutes_out >= 30:
        reason = f"Temperature out of range for {minutes_out} min"

    if status == "UNSAFE" and minutes_out >= 60:
        reason = f"Temperature out of range for {minutes_out} min"

    payload = {
        "bag_id": bid,
        "timestamp": datetime.now().isoformat(),
        "blood_type": row["blood_type"],
        "route": row["route"],
        "predicted_health_index": hi,
        "status": status,
        "temp_mean": row["temp_mean"],
        "hum_mean": row["hum_mean"],
        "accel_rms": row["accel_rms"],
        "door_count": row["door_count"],
        "card_reason": reason,
    }

    history.append(payload)
    HISTORY_PATH.write_text(json.dumps(history[-20000:], indent=2))
    return payload

@app.get("/snapshot")
def snapshot():
    return {
        "server_time": datetime.now().isoformat(),
        "interval_seconds": INTERVAL_SECONDS,
        "bags": [predict_one(bid) for bid in BAG_IDS],
    }
@app.get("/history/{bag_id}")
def get_history(bag_id: str):
    if not HISTORY_PATH.exists():
        return {"bag_id": bag_id, "records": []}

    try:
        data = json.loads(HISTORY_PATH.read_text())
    except Exception:
        return {"bag_id": bag_id, "records": []}

    records = [r for r in data if r.get("bag_id") == bag_id]
    return {
        "bag_id": bag_id,
        "records": records[-500:]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
