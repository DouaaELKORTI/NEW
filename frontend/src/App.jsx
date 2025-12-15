import React, { useEffect, useMemo, useState } from "react";
import BagGrid from "./components/BagGrid.jsx";
import DetailsPanel from "./components/DetailsPanel.jsx";
import Navbar from "./components/Navbar.jsx";
import "./App.css";

const API = "http://localhost:8000";

export default function App() {
  const [snapshot, setSnapshot] = useState(null);
  const [selectedBag, setSelectedBag] = useState(null);

  // polling every 15s
  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const res = await fetch(`${API}/snapshot`);
        const data = await res.json();
        if (!cancelled) {
          setSnapshot(data);
          if (!selectedBag && data?.bags?.length) {
            setSelectedBag(data.bags[0].bag_id);
          }
        }
      } catch (e) {
        console.error("snapshot error", e);
      }
    };

    load();
    const t = setInterval(load, 15000);
    return () => {
      cancelled = true;
      clearInterval(t);
    };
  }, [selectedBag]);

  const bags = snapshot?.bags ?? [];
  const selectedRow = useMemo(
    () => bags.find((b) => b.bag_id === selectedBag) || null,
    [bags, selectedBag]
  );

  // history for selected bag (from backend)
  const [history, setHistory] = useState([]);
  useEffect(() => {
    let cancelled = false;
    const loadHist = async () => {
      if (!selectedBag) return;
      try {
        const res = await fetch(`${API}/history/${selectedBag}`);
        const data = await res.json();
        if (!cancelled) setHistory(data.records || []);
      } catch (e) {
        console.error("history error", e);
      }
    };
    loadHist();
    const t = setInterval(loadHist, 15000);
    return () => {
      cancelled = true;
      clearInterval(t);
    };
  }, [selectedBag]);

  return (
    <div className="app-shell">
      <Navbar
        serverTime={snapshot?.server_time}
        bagsCount={bags.length}
      />

      <div className="layout">
        <div className="left">
          <BagGrid
            bags={bags}
            selectedBag={selectedBag}
            setSelectedBag={setSelectedBag}
          />
        </div>

        <div className="right">
          <DetailsPanel
            row={selectedRow}
            history={history}
            sampleIntervalSeconds={snapshot?.interval_seconds ?? 15}
          />
        </div>
      </div>
    </div>
  );
}
