import React from "react";
import BagCard from "./BagCard.jsx";

export default function BagGrid({ bags, selectedBag, setSelectedBag }) {
  return (
    <div className="grid-wrap">
      <div className="grid-title">Blood Bags</div>

      <div className="grid">
        {bags.map((b) => (
          <BagCard
            key={b.bag_id}
            bag={b}
            selected={b.bag_id === selectedBag}
            onClick={() => setSelectedBag(b.bag_id)}
          />
        ))}
      </div>
    </div>
  );
}
