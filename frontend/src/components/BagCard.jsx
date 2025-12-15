import React, { useMemo } from "react";
import QRCode from "react-qr-code";

function statusClass(status) {
  if (status === "SAFE") return "safe";
  if (status === "WARNING") return "warning";
  return "unsafe";
}

export default function BagCard({ bag, selected, onClick }) {
  const qrValue = useMemo(() => {
    return JSON.stringify({
      bag_id: bag.bag_id,
      blood_type: bag.blood_type,
      health_index: Number(bag.predicted_health_index).toFixed(4),
      status: bag.status,
      temp_mean: bag.temp_mean,
      hum_mean: bag.hum_mean,
      accel_rms: bag.accel_rms,
      door_count: bag.door_count,
      timestamp: bag.timestamp,
    });
  }, [bag]);

  return (
    <button
      className={`bag-card ${statusClass(bag.status)} ${selected ? "selected" : ""}`}
      onClick={onClick}
    >
      <div className="qr-box">
        <QRCode value={qrValue} size={120} />
      </div>

      <div className="bag-id">{bag.bag_id}</div>

      <div className="hi-row">
        <span className="hi">{Number(bag.predicted_health_index).toFixed(3)}</span>
        <span className={`badge ${statusClass(bag.status)}`}>{bag.status}</span>
      </div>

      <div className="mini">
        <span>🌡 {Number(bag.temp_mean).toFixed(2)}°C</span>
        <span>💧 {Number(bag.hum_mean).toFixed(1)}%</span>
      </div>
    </button>
  );
}
