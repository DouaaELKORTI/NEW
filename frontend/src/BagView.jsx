// src/BagView.jsx
import { useEffect, useState } from "react";
import { bagsData } from "./data/simulatedBags.js";

export default function BagView() {
  const [bag, setBag] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const bag_id = params.get("id");
    const t = Number(params.get("t"));

    if (!bag_id) return;

    const base = bagsData.find(b => b.id === bag_id);
    if (!base) return;

    const record = {
      ...base,
      temp: base.tempBase + Math.sin(t / 5) * 0.3,
      health: base.healthBase - t * 0.0005,
      vibration: Math.abs(Math.sin(t / 7)) * 0.1,
      timeIndex: t,
    };

    setBag(record);
  }, []);

  if (!bag) return <p style={{ color: "white" }}>Loading...</p>;

  return (
    <div style={{ padding: 20, color: "white", maxWidth: 450, margin: "auto" }}>
      <h2>Bag Information — {bag.id}</h2>

      <p><strong>Time:</strong> t = {bag.timeIndex}</p>
      <p><strong>Temp:</strong> {bag.temp.toFixed(2)}°C</p>
      <p><strong>Health Index:</strong> {bag.health.toFixed(3)}</p>
      <p><strong>Vibration:</strong> {bag.vibration.toFixed(3)}</p>

      <p style={{ fontWeight: "bold", color: bag.health < 0.92 ? "red" : "lightgreen" }}>
        {bag.health < 0.92 ? "⚠ CONDITION CRITICAL" : "SAFE"}
      </p>
    </div>
  );
}
