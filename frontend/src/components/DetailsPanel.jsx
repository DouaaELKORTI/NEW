import React from "react";
import HistoryChart from "./HistoryChart.jsx";

export default function DetailsPanel({ row, history, sampleIntervalSeconds }) {
  if (!row) {
    return (
      <div className="panel">
        <div className="panel-title">Bag Details</div>
        <div className="panel-empty">Select a bag.</div>
      </div>
    );
  }

  return (
    <div className="panel">
      <div className="panel-title">Bag Overview</div>

      <div className="head">
        <div>
          <div className="big">{row.bag_id}</div>

          {/* Blood type emphasized */}
          <div className="blood-type-big">
            {row.blood_type}
          </div>

          <div className="muted">
            Updated: {new Date(row.timestamp).toLocaleString()}
          </div>
        </div>

        <div className="hi-big">
          <div className="hi-number">
            {Number(row.predicted_health_index).toFixed(4)}
          </div>
          <div className={`hi-status ${row.status.toLowerCase()}`}>
            {row.status}
          </div>
        </div>
      </div>

      <div className="kpis">
        <div className="kpi">
          <span>Mean Temperature</span>
          <b>{Number(row.temp_mean).toFixed(2)} C</b>
        </div>
        <div className="kpi">
          <span>Mean Humidity</span>
          <b>{Number(row.hum_mean).toFixed(1)} %</b>
        </div>
        <div className="kpi">
          <span>Mean Vibration</span>
          <b>{Number(row.accel_rms).toFixed(3)}</b>
        </div>
      </div>

      <div className="charts">
        <HistoryChart
          title="Health Index (Last records)"
          field="predicted_health_index"
          records={history}
        />
        <HistoryChart
          title="Temperature"
          field="temp_mean"
          records={history}
        />
        <HistoryChart
          title="Humidity"
          field="hum_mean"
          records={history}
        />
        <HistoryChart
          title="Door Count"
          field="door_count"
          records={history}
        />
        <HistoryChart
          title="Vibration"
          field="accel_rms"
          records={history}
        />
      </div>

      <div className="muted foot">
        Sample interval: {sampleIntervalSeconds}s · History points:{" "}
        {history?.length ?? 0}
      </div>
    </div>
  );
}
