# ATLAS — Adaptive Traffic Light & Analytics System

ATLAS is a smart traffic control system that combines real-time traffic
prediction with automated signal and routing decisions. It's built as two
cooperating services: a **prediction API** that forecasts congestion on each
road segment, and a **control API** that turns those forecasts into signal
timing, route guidance, and emergency corridor decisions.

## Architecture

```
┌─────────────────────┐        ┌──────────────────────┐
│   Prediction API     │  --->  │     Control API       │
│  (Node.js, :5000)    │        │  (FastAPI, :8001)      │
│  Traffic forecasting │        │  Signals, routing,     │
│  per road segment     │        │  emergency corridors,  │
└─────────────────────┘        │  what-if simulation    │
                                └──────────────────────┘
```

The control API consumes live forecasts from the prediction API through an
adapter layer, which normalizes field names and value scales so the two
services can evolve independently. If the prediction API is unreachable, the
control API automatically falls back to mock data so development and demos
can continue uninterrupted.

## Repository Layout

```
atlas/
├── backend/
│   ├── atlas_prediction/     # Traffic prediction service (Node.js)
│   └── atlas_control/        # Traffic control service (FastAPI/Python)
└── frontend/                 # Dashboard UI
```

## Getting Started

### Prerequisites
- Node.js and npm
- Python 3.9+

### 1. Start the prediction service
```bash
cd backend/atlas_prediction
npm install
node server.js
```
Runs at `http://localhost:5000`.

### 2. Start the control service
```bash
cd backend/atlas_control
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

python3 test_api.py                   # optional: run automated checks
uvicorn app.main:app --reload --port 8001
```
Runs at `http://localhost:8001`. Interactive API docs are available at
`http://localhost:8001/docs`.

> The control service works independently of the prediction service. If the
> prediction API isn't running, it automatically falls back to mock data
> (a warning is printed in the terminal), so the control service can still be
> developed, tested, and demoed on its own.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/control` | GET | Signal timing and routing decisions for every monitored road, based on live traffic forecasts |
| `/api/route` | GET | Shortest route between two segments (e.g. `?start=SEG-101&end=SEG-105`), avoiding severe congestion |
| `/api/emergency` | POST | Activates a green-light corridor for an emergency vehicle |
| `/api/network` | GET | Road segment coordinates for the dashboard map |
| `/api/whatif` | POST | Digital-twin simulation of traffic, weather, events, or signal changes |

## The Prediction Adapter

The prediction service and control service were designed against slightly
different data conventions — different field names, and a 0–100 congestion
scale versus a 0–1 scale used internally by the control service.
`app/prediction_adapter.py` is the single translation layer between the two:
it's the only file that needs to change if the prediction API's output
format changes, keeping the rest of the control service decoupled from that
detail.

## Road Network

The system monitors five road segments, `SEG-101` through `SEG-105`,
defined in `app/network.py`.

## Testing

Run the automated test suite at any time, no servers required:
```bash
python3 test_api.py
```
This runs 14 checks covering the core control logic.
