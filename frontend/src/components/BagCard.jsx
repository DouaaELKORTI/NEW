import React, { useMemo } from "react";
import QRCode from "react-qr-code";

function statusClass(status) {
  if (status === "SAFE") return "safe";
  if (status === "WARNING") return "warning";
  return "unsafe";
}

export default function BagCard({ bag, selected, onClick }) {
  const qrValue = useMemo(() => {
    return (
      `Bag ID: ${bag.bag_id}\n` +
      `Blood Type: ${bag.blood_type}\n` +
      `Health Index: ${Number(bag.predicted_health_index).toFixed(4)}\n` +
      `Status: ${bag.status}\n` +
      `Mean Temperature (C): ${Number(bag.temp_mean).toFixed(2)}\n` +
      `Mean Humidity (%): ${Number(bag.hum_mean).toFixed(1)}\n` +
      `Mean Vibration: ${Number(bag.accel_rms).toFixed(3)}\n` +
      `Door Count: ${bag.door_count}\n` +
      `Timestamp: ${new Date(bag.timestamp).toISOString()}`
    );
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
        <span> {Number(bag.temp_mean).toFixed(2)}°C</span>
        <span> {Number(bag.hum_mean).toFixed(1)}%</span>
      </div>
    </button>
  );
}
