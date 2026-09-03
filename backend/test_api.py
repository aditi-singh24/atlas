"""
ATLAS Traffic Control — Automated Test Script

Run this any time you change code, to instantly check nothing broke.
This does NOT need the server running separately — it tests your
functions directly, which is faster and more reliable for development.

Usage:
    python3 test_api.py
"""

import sys
from app.mock_predictions import generate_mock_predictions
from app.control_engine import decide_all_signals, recommend_route, activate_green_corridor
from app.whatif_engine import WhatIfScenario, run_simulation, summarize_simulation
from app.schema import EmergencyVehicle
from app.network import all_road_ids


PASS = "✅ PASS"
FAIL = "❌ FAIL"
failures = []


def check(name, condition):
    status = PASS if condition else FAIL
    print(f"{status}  {name}")
    if not condition:
        failures.append(name)


def run_tests():
    print("=" * 50)
    print("ATLAS Traffic Control — Test Suite")
    print("=" * 50)

    # 1. Predictions generate for every road
    predictions = generate_mock_predictions()
    check(
        "Predictions generated for all roads",
        len(predictions) == len(all_road_ids())
    )
    check(
        "Every prediction has a valid congestion score (0-1)",
        all(0 <= p.congestion_score <= 1 for p in predictions)
    )

    # 2. Control decisions
    controls = decide_all_signals(predictions)
    check(
        "Control decision generated for every road",
        len(controls) == len(predictions)
    )
    check(
        "Every control output has a non-empty recommended_route",
        all(len(c.recommended_route) > 0 for c in controls)
    )
    check(
        "HIGH/SEVERE congestion roads get GREEN_EXTENDED",
        all(
            c.signal_state == "GREEN_EXTENDED"
            for c, p in zip(controls, predictions)
            if p.congestion_level in ("HIGH", "SEVERE")
        )
    )

    # 3. Routing
    route = recommend_route("SEG-101", "SEG-104", predictions)
    check(
        "Route from SEG-101 to SEG-104 starts at SEG-101",
        route[0] == "SEG-101"
    )
    check(
        "Route from SEG-101 to SEG-104 ends at SEG-104",
        route[-1] == "SEG-104"
    )
    same_route = recommend_route("SEG-103", "SEG-103", predictions)
    check(
        "Route to the same road returns immediately",
        same_route == ["SEG-103"]
    )

    # 4. Emergency corridor
    vehicle = EmergencyVehicle(
        vehicle_id="AMB-TEST",
        current_road="SEG-101",
        destination_road="SEG-105",
        priority=True,
    )
    corridor = activate_green_corridor(vehicle, predictions)
    check(
        "Emergency corridor produces at least one road",
        len(corridor) > 0
    )
    check(
        "Every road in the corridor is GREEN_EXTENDED with priority",
        all(c.signal_state == "GREEN_EXTENDED" and c.emergency_priority for c in corridor)
    )

    # 5. What-if simulation
    scenario = WhatIfScenario(
        traffic_volume_change_pct=20,
        rain=True,
        event=True,
        signal_timing_change_sec=15,
    )
    results = run_simulation(predictions, scenario)
    summary = summarize_simulation(results)
    check(
        "Simulation produces a result for every road",
        len(results) == len(predictions)
    )
    check(
        "Adding traffic/rain/event increases average congestion",
        summary["simulated_congestion_pct"] > summary["current_congestion_pct"]
    )
    check(
        "All simulated scores stay within 0-100%",
        all(0 <= r.simulated_congestion_score <= 1 for r in results)
    )

    # Extra signal time alone should REDUCE congestion, all else equal
    calmer_scenario = WhatIfScenario(signal_timing_change_sec=60)
    calmer_results = run_simulation(predictions, calmer_scenario)
    calmer_summary = summarize_simulation(calmer_results)
    check(
        "Extra signal time alone reduces average congestion",
        calmer_summary["simulated_congestion_pct"] < calmer_summary["current_congestion_pct"]
    )

    # ------------------------------------------------------------------
    print("=" * 50)
    if failures:
        print(f"{len(failures)} test(s) FAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All tests passed. Person B backend is verified working.")
        print("=" * 50)


if __name__ == "__main__":
    run_tests()
