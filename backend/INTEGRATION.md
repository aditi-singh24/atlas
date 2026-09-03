# ATLAS — Integration Guide (for the dashboard/Person A)

Person B's backend is complete and tested. This doc is for whoever connects
to it — the dashboard team, or Person A once their real predictions are ready.

## Base URL
Local development: `http://localhost:8001` (or whatever port it's run on)

## Connecting the dashboard (JavaScript / React example)

```javascript
// Get signal + route decisions for every road
async function getControlDecisions() {
  const res = await fetch("http://localhost:8001/api/control");
  return await res.json();
}

// Get a recommended route between two roads
async function getRoute(start, end) {
  const res = await fetch(`http://localhost:8001/api/route?start=${start}&end=${end}`);
  return await res.json();
}

// Run a what-if simulation
async function runWhatIf(scenario) {
  const res = await fetch("http://localhost:8001/api/whatif", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(scenario),
  });
  return await res.json();
}
// Example call:
// runWhatIf({ traffic_volume_change_pct: 20, rain: true, event: true, signal_timing_change_sec: 15 })

// Trigger an emergency green corridor
async function triggerEmergency(vehicle) {
  const res = await fetch("http://localhost:8001/api/emergency", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(vehicle),
  });
  return await res.json();
}
// Example call:
// triggerEmergency({ vehicle_id: "AMB-01", current_road: "R004", destination_road: "R010", priority: true })

// Get road coordinates for the map
async function getNetwork() {
  const res = await fetch("http://localhost:8001/api/network");
  return await res.json();
}
```

Note: CORS is already enabled on the backend (`allow_origins=["*"]`), so
these calls will work from any dashboard origin without extra config.

## Connecting Person A's real predictions

Right now, Person B's backend generates its own **mock** predictions so it
can run independently. Once Person A's real `/api/predictions` endpoint exists:

1. Open `app/main.py`
2. Find this function:
   ```python
   def fetch_predictions() -> list[PredictionOutput]:
       return generate_mock_predictions()
   ```
3. Replace it with:
   ```python
   import requests

   def fetch_predictions() -> list[PredictionOutput]:
       res = requests.get("http://<person-a-host>:<port>/api/predictions")
       return [PredictionOutput(**item) for item in res.json()]
   ```
4. That's the only change needed. Every endpoint downstream
   (`/api/control`, `/api/route`, `/api/whatif`, `/api/emergency`) already
   expects data shaped like `PredictionOutput` — nothing else breaks.

## What roads exist right now (mock/demo network)
10 roads: R001–R010, connected as a small city grid.
See `app/network.py` for the exact graph and coordinates — replace this
with a real map/GPS network later if there's time.

## Verifying it's working
Run `python3 test_api.py` any time — it checks all logic directly (no
server needed) and prints pass/fail for 14 checks covering every endpoint.
