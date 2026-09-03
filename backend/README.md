# ATLAS Traffic Control API — Person B (COMPLETE + CONNECTED TO PERSON A)

This backend is fully connected to Person A's real Node.js prediction API.
An adapter translates their actual output shape into what this system needs,
so neither of you had to rewrite already-working code.

## Setup (run once)
```bash
cd atlas_control
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run — TWO servers need to be running together

**Terminal 1 — Person A's prediction server (Node.js):**
```bash
cd atlas_prediction    # Person A's project folder
npm install
node server.js
```
Runs on http://localhost:5000

**Terminal 2 — Person B's control server (this project):**
```bash
cd atlas_control
source venv/bin/activate
python3 test_api.py                          # optional: confirms logic works
uvicorn app.main:app --reload --port 8001
```
Runs on http://localhost:8001

If Person A's server isn't running, Person B's server automatically falls
back to mock data (check the terminal for a warning) — so you can still
develop and demo Person B's half independently.

Then open: http://localhost:8001/docs

## Endpoints
| Endpoint | Method | Purpose |
|---|---|---|
| `/api/control` | GET | Signal + route decision for every road (pulls live from Person A) |
| `/api/route?start=SEG-101&end=SEG-105` | GET | Shortest route avoiding severe congestion |
| `/api/emergency` | POST | Activates green corridor for an emergency vehicle |
| `/api/network` | GET | Road coordinates for the dashboard map |
| `/api/whatif` | POST | Digital twin — simulate traffic/rain/event/signal changes |

## The Adapter (app/prediction_adapter.py)
Person A's real API returns a different shape than the schema you two
originally agreed on (different field names, 0-100 scale instead of 0-1,
etc). Rather than rewriting either side, `prediction_adapter.py` translates
between them at the boundary. This is the ONLY file that knows about both
shapes — if Person A's output format ever changes, this is the only file
to update.

## Road network
Aligned with Person A's real 5 monitored segments: SEG-101 through SEG-105
(see `app/network.py`).

## Verifying it's working
Run `python3 test_api.py` any time — 14 automated checks, no server needed.
