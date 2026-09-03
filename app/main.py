"""
ATLAS — Traffic Control API (Person B)

Run with:
    uvicorn app.main:app --reload --port 8001

Docs auto-generated at:
    http://localhost:8001/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schema import PredictionOutput, ControlOutput, EmergencyVehicle
from app.control_engine import decide_all_signals, recommend_route, activate_green_corridor
from app.mock_predictions import generate_mock_predictions
from app.network import all_road_ids, ROAD_COORDS
from app.whatif_engine import WhatIfScenario, run_simulation, summarize_simulation
from app.prediction_adapter import adapt_predictions

import requests

PERSON_A_URL = "http://localhost:5000/api/predictions"

app = FastAPI(title="ATLAS Traffic Control API", version="0.1.0")

# Allow the dashboard (any origin, for hackathon simplicity) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# THE ONLY PLACE YOU'LL NEED TO CHANGE once Person A's real API is live:
# replace generate_mock_predictions() with a call to their endpoint.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Connects to Person A's real Node.js prediction API (localhost:5000).
# Falls back to mock data automatically if that server isn't running,
# so this API keeps working during development even before Person A starts theirs.
# ---------------------------------------------------------------------------

def fetch_predictions() -> list[PredictionOutput]:
    try:
        res = requests.get(PERSON_A_URL, timeout=2)
        res.raise_for_status()
        return adapt_predictions(res.json())
    except Exception:
        # Person A's server isn't reachable — use mock data so development
        # and demos keep working. Check the terminal for this warning.
        print(f"[ATLAS] Could not reach Person A's API at {PERSON_A_URL} — using mock predictions.")
        return generate_mock_predictions()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ATLAS Traffic Control API is running"}


@app.get("/api/control", response_model=list[ControlOutput])
def get_control_decisions():
    """
    Main deliverable: pulls predictions (mock or real) and returns
    a signal/route decision for every road segment.
    """
    predictions = fetch_predictions()
    return decide_all_signals(predictions)


@app.get("/api/route")
def get_route(start: str, end: str):
    """
    Recommend a route between two road segments, avoiding severe congestion.
    Example: /api/route?start=R001&end=R010
    """
    if start not in all_road_ids() or end not in all_road_ids():
        raise HTTPException(status_code=404, detail="Unknown road_id")

    predictions = fetch_predictions()
    route = recommend_route(start, end, predictions)
    return {"start": start, "end": end, "route": route}


@app.post("/api/emergency", response_model=list[ControlOutput])
def trigger_emergency_corridor(vehicle: EmergencyVehicle):
    """
    Activates a green corridor for an emergency vehicle.
    Send a body like:
    {
      "vehicle_id": "AMB-01",
      "current_road": "R004",
      "destination_road": "R010",
      "priority": true
    }
    """
    if vehicle.current_road not in all_road_ids() or vehicle.destination_road not in all_road_ids():
        raise HTTPException(status_code=404, detail="Unknown road_id")

    predictions = fetch_predictions()
    return activate_green_corridor(vehicle, predictions)


@app.get("/api/network")
def get_network():
    """Returns road segment coordinates, for the dashboard's map view."""
    return ROAD_COORDS


@app.post("/api/whatif")
def what_if_simulation(scenario: WhatIfScenario):
    """
    Digital Twin — recalculates congestion under a hypothetical scenario
    and returns a current-vs-simulated comparison, matching the dashboard's
    What-If panel (Traffic Volume / Rain / Event / Signal Timing).

    Example request body:
    {
      "traffic_volume_change_pct": 20,
      "rain": true,
      "event": true,
      "signal_timing_change_sec": 15
    }
    """
    predictions = fetch_predictions()
    results = run_simulation(predictions, scenario)
    summary = summarize_simulation(results)

    return {
        "scenario": scenario,
        "summary": summary,
        "per_road": results,
    }
