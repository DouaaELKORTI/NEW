import React, { useEffect, useRef } from 'react';
import QRCode from 'qrcode';

const QrDisplay = ({ bagId, healthIndex, temp, humidity, timestamp }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const qrData = JSON.stringify({
      bag_id: bagId,
      health_index: healthIndex.toFixed(4),
      temperature: temp ? temp.toFixed(1) : null,
      humidity: humidity ? humidity.toFixed(1) : null,
      last_updated: timestamp,
      facility: "BloodBank_AI_Monitor",
      status: healthIndex >= 0.7 ? 'SAFE' : 'CHECK_REQUIRED'
    }, null, 2);

    // Generate QR code with gradient
    QRCode.toCanvas(canvasRef.current, qrData, {
      width: 200,
      margin: 1,
      color: {
        dark: healthIndex >= 0.8 ? '#00E676' : 
               healthIndex >= 0.6 ? '#FFB300' : '#FF5252',
        light: '#FFFFFF'
      },
      errorCorrectionLevel: 'H'
    }, (error) => {
      if (error) console.error('QR generation error:', error);
    });
  }, [bagId, healthIndex, temp, humidity, timestamp]);

  return (
    <div className="qr-display">
      <canvas ref={canvasRef} />
      <div className="qr-footer">
        <div className="qr-indicator">
          <div 
            className="qr-dot" 
            style={{
              backgroundColor: healthIndex >= 0.8 ? '#00E676' : 
                               healthIndex >= 0.6 ? '#FFB300' : '#FF5252'
            }}
          ></div>
          <span>Scan for real-time data</span>
        </div>
      </div>
    </div>
  );
};

export default QrDisplay;