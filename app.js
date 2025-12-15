// Load data
async function loadBags() {
    const res = await fetch("data/data.json");
    const bags = await res.json();
  
    // We only show 6 bags
    const six = bags.slice(0, 6);
  
    renderQRCodes(six);
    updateTimestamp();
  }
  
  // Render the 6 QR codes
  function renderQRCodes(bags) {
    const container = document.getElementById("bags-container");
    container.innerHTML = "";
  
    bags.forEach((bag, index) => {
      const block = document.createElement("div");
      block.className = "bag-block";
      block.onclick = () => showDetails(bag);
  
      const qrID = `qr-${index}`;
  
      block.innerHTML = `
        <canvas id="${qrID}" class="qr-box"></canvas>
        <div class="bag-label">bag_id : ${bag.bag_id}</div>
      `;
  
      container.appendChild(block);
  
      // QR CONTENT (dynamic)
      const payload = JSON.stringify({
        bag_id: bag.bag_id,
        blood_type: bag.blood_type,
        health_index: bag.health_index,
        temperature: bag.temperature,
        humidity: bag.humidity,
        vibration: bag.vibration,
        anomaly: bag.anomaly,
        timestamp: bag.timestamp
      });
  
      // Create QR (WITH DELAY because DOM needs to render first)
      setTimeout(() => {
        new QRious({
          element: document.getElementById(qrID),
          value: payload,
          size: 180,
          background: "#ffffff",
          foreground: "#000000"
        });
      }, 80);
    });
  }
  
  // Show details in sidebar
  function showDetails(bag) {
    document.getElementById("details-content").innerHTML = `
      <h3>${bag.bag_id} (${bag.blood_type})</h3>
  
      <div><strong>Health Index:</strong> ${bag.health_index}</div>
      <div><strong>Temperature:</strong> ${bag.temperature}°C</div>
      <div><strong>Humidity:</strong> ${bag.humidity}%</div>
      <div><strong>Vibration:</strong> ${bag.vibration}</div>
      <div><strong>Anomaly:</strong> ${bag.anomaly ? "YES ⚠️" : "NO"}</div>
      <div><strong>Last Update:</strong> ${bag.timestamp}</div>
    `;
  }
  
  // Update time
  function updateTimestamp() {
    document.getElementById("last-update").textContent =
      "Last update: " + new Date().toLocaleString();
  }
  
  // Auto refresh every 5s (simulate real-time IoT)
  setInterval(loadBags, 5000);
  
  loadBags();
  