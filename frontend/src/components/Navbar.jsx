import React from "react";

export default function Navbar({ serverTime, bagsCount }) {
  const timeText = serverTime ? new Date(serverTime).toLocaleString() : "—";

  return (
    <div className="navbar">
      <div className="brand">
        <span className="dot"></span>
        <div>
          <div className="title">AI Blood Storage Monitor</div>
          <div className="subtitle">Real-time · Dynamic E-Ink QR · Bag-level Quality</div>
        </div>
      </div>

      <div className="meta">
        <div><b>Bags:</b> {bagsCount}</div>
        <div><b>Server:</b> {timeText}</div>
      </div>
    </div>
  );
}
