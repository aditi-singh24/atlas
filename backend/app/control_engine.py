"""
ATLAS — Traffic Control Engine (Person B's core deliverable)

Takes PredictionOutput (from Person A) as input, and decides:
  - signal state per road
  - a recommended route between two points
  - whether an emergency green corridor should activate

This is deliberately rule-based (no ML) — fast to build, easy to explain
in a demo, and easy to extend later if you have time.
"""

from collections import deque
from app.schema import PredictionOutput, ControlOutput, SignalState, EmergencyVehicle
from app.network import neighbors, all_road_ids


# ---------------------------------------------------------------------------
# 1. Signal decision — the core "if congestion X, do Y" logic
# ---------------------------------------------------------------------------

def decide_signal(prediction: PredictionOutput) -> ControlOutput:
    """
    Turns one road's congestion prediction into a signal decision.
    This is the heart of Person B's system.
    """
    level = prediction.congestion_level
    score = prediction.congestion_score

    if level == "SEVERE":
        signal_state = SignalState.GREEN_EXTENDED
        reason = "severe_congestion_predicted"
    elif level == "HIGH":
        signal_state = SignalState.GREEN_EXTENDED
        reason = "high_congestion_predicted"
    elif level == "MEDIUM":
        signal_state = SignalState.GREEN
        reason = "moderate_congestion_normal_cycle"
    else:  # LOW
        signal_state = SignalState.GREEN
        reason = "low_congestion_normal_cycle"

    route = find_route(prediction.road_id, _least_congested_neighbor(prediction.road_id))

    return ControlOutput(
        road_id=prediction.road_id,
        signal_state=signal_state,
        recommended_route=route,
        emergency_priority=False,
        reason=reason,
    )


def decide_all_signals(predictions: list[PredictionOutput]) -> list[ControlOutput]:
    return [decide_signal(p) for p in predictions]


def _least_congested_neighbor(road_id: str) -> str:
    """Placeholder heuristic — picks first neighbor. Route scoring can
    be improved later by factoring in each neighbor's congestion score."""
    n = neighbors(road_id)
    return n[0] if n else road_id


# ---------------------------------------------------------------------------
# 2. Route recommendation — simple BFS shortest path over the road graph
# ---------------------------------------------------------------------------

def find_route(start: str, end: str) -> list[str]:
    """Breadth-first search shortest path (by hop count) from start to end."""
    if start == end:
        return [start]
    if start not in all_road_ids() or end not in all_road_ids():
        return [start]

    visited = {start}
    queue = deque([[start]])

    while queue:
        path = queue.popleft()
        current = path[-1]

        for nxt in neighbors(current):
            if nxt == end:
                return path + [nxt]
            if nxt not in visited:
                visited.add(nxt)
                queue.append(path + [nxt])

    return [start]  # no path found


def recommend_route(start: str, end: str, predictions: list[PredictionOutput]) -> list[str]:
    """
    Route recommendation that avoids SEVERE congestion roads where possible.
    Falls back to shortest path if every route is congested.
    """
    if start == end:
        return [start]

    congestion_map = {p.road_id: p.congestion_level for p in predictions}

    def is_severe(road_id: str) -> bool:
        return congestion_map.get(road_id) == "SEVERE"

    # Try BFS while skipping SEVERE roads first
    visited = {start}
    queue = deque([[start]])

    while queue:
        path = queue.popleft()
        current = path[-1]

        for nxt in neighbors(current):
            if nxt == end:
                return path + [nxt]
            if nxt not in visited and not is_severe(nxt):
                visited.add(nxt)
                queue.append(path + [nxt])

    # fallback: allow severe roads, just find any path
    return find_route(start, end)


# ---------------------------------------------------------------------------
# 3. Green corridor / emergency vehicle priority
# ---------------------------------------------------------------------------

def activate_green_corridor(vehicle: EmergencyVehicle, predictions: list[PredictionOutput]) -> list[ControlOutput]:
    """
    Given an ambulance/emergency vehicle, finds its route and forces every
    road along that route to GREEN_EXTENDED with emergency_priority=True.
    """
    route = recommend_route(vehicle.current_road, vehicle.destination_road, predictions)

    outputs = []
    for road_id in route:
        outputs.append(
            ControlOutput(
                road_id=road_id,
                signal_state=SignalState.GREEN_EXTENDED,
                recommended_route=route,
                emergency_priority=True,
                reason=f"emergency_corridor_for_{vehicle.vehicle_id}",
            )
        )
    return outputs
