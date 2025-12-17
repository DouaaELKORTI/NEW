# AI Blood Storage Monitor

A full-stack AI-powered system for real-time monitoring of blood bags during storage and transport.
The system combines IoT-like sensor data with AutoGluon machine learning models and a modern React dashboard.

---

## Features

- Real-time blood bag monitoring
- AI-based Health Index prediction (AutoGluon)
- FastAPI backend
- React + Vite frontend
- Dynamic QR codes per blood bag
- Time-series visualization (health, temperature, humidity, vibration)
- Medical-grade dark UI

---

## Project Structure

AI-Blood-Storage-Monitor/
├── backend/        # FastAPI backend + AI inference
├── frontend/       # React (Vite) dashboard
├── .gitignore
├── README.md
└── LICENSE

---

## Requirements

Backend:
- Python 3.10 or 3.11
- pip

Frontend:
- Node.js (LTS recommended)
- npm

---

## Backend Setup (FastAPI + AutoGluon)

Open a terminal in the project root and run:

cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

If you are on Windows and AutoGluon fails, run:

pip install --upgrade --force-reinstall --no-cache-dir lightgbm
pip install --upgrade --force-reinstall --no-cache-dir autogluon.tabular

Run the backend server:

uvicorn app:app --reload --host 127.0.0.1 --port 8000

Test backend in browser:
http://127.0.0.1:8000/health
http://127.0.0.1:8000/snapshot

---

## Frontend Setup (React + Vite)

Open a new terminal and run:

cd frontend
npm install
npm run dev

Open the application in your browser:
http://localhost:5173

Make sure the backend is running before starting the frontend.

---

## Notes

- venv/ and node_modules/ are ignored by Git
- Backend runs on port 8000
- Frontend runs on port 5173

---

## License

MIT License

---

## Author

Douaa EL KORTI
