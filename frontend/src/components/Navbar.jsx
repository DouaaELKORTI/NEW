import React, { useEffect, useState } from "react";

export default function Navbar({ serverTime, bagsCount }) {
  const [now, setNow] = useState(
    serverTime ? new Date(serverTime) : new Date()
  );

  // Sync with server time when it changes
  useEffect(() => {
    if (serverTime) {
      setNow(new Date(serverTime));
    }
  }, [serverTime]);

  // Real-time ticking clock
  useEffect(() => {
    const t = setInterval(() => {
      setNow((prev) => new Date(prev.getTime() + 1000));
    }, 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="navbar modern">
      <div className="nav-left">
        <div className="status-dot" />
        <div className="titles">
          <div className="title">
            AI Blood Storage Monitor
            <span className="tech-tag">E-Ink</span>
          </div>
          <div className="subtitle">
            Real-time monitoring · Bag-level quality intelligence
          </div>
        </div>
      </div>

      <div className="nav-right">
        <div className="clock">
          {now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
        </div>
        <div className="meta">
          <span>{now.toLocaleDateString()}</span>
          <span>•</span>
          <span>{bagsCount} bags</span>
        </div>
      </div>
    </div>
  );
}
