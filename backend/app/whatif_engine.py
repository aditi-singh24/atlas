"""
ATLAS — What-If Digital Twin (Person B's third deliverable)

Takes the CURRENT predictions and a hypothetical scenario (more traffic,
rain, an event, extra signal time), recalculates what congestion WOULD
look like under those conditions, and returns a before/after comparison.

This does not call any external simulation library — it's a transparent,
explainable formula, which is actually better for a hackathon demo because
you can explain exactly why the numbers changed.
"""

from pydantic import BaseModel
from typing import Optional
from app.schema import PredictionOutput, CongestionLevel


class WhatIfScenario(BaseModel):
    traffic_volume_change_pct: float = 0     # e.g. 20 means +20%
    rain: bool = False
    event: bool = False
    signal_timing_change_sec: int = 0        # e.g. +15 seconds green


class RoadSimulationResult(BaseModel):
    road_id: str
    current_congestion_score: float
    current_congestion_level: CongestionLevel
    simulated_congestion_score: float
    simulated_congestion_level: CongestionLevel
    current_avg_speed_kmh: float
    simulated_avg_speed_kmh: float


def _score_to_level(score: float) -> CongestionLevel:
    if score < 0.35:
        return CongestionLevel.LOW
    elif score < 0.6:
        return CongestionLevel.MEDIUM
    elif score < 0.8:
        return CongestionLevel.HIGH
    return CongestionLevel.SEVERE


def _score_to_speed(score: float) -> float:
    """Rough model: higher congestion score = lower average speed.
    0 congestion -> ~50 km/h free flow. 1.0 congestion -> ~5 km/h crawl."""
    return round(50 - (score * 45), 1)


def run_simulation(
    predictions: list[PredictionOutput],
    scenario: WhatIfScenario,
) -> list[RoadSimulationResult]:
    results = []

    for p in predictions:
        score = p.congestion_score

        # Traffic volume increase raises congestion roughly proportionally
        score += (scenario.traffic_volume_change_pct / 100) * 0.5

        # Rain adds a flat congestion bump (slower speeds, more caution)
        if scenario.rain:
            score += 0.12

        # An event (concert, match, roadwork) adds another bump
        if scenario.event:
            score += 0.15

        # Extra green signal time reduces congestion slightly
        # (more throughput per cycle)
        score -= (scenario.signal_timing_change_sec / 60) * 0.2

        # clamp between 0 and 1
        sim_score = max(0.0, min(1.0, round(score, 2)))

        results.append(
            RoadSimulationResult(
                road_id=p.road_id,
                current_congestion_score=p.congestion_score,
                current_congestion_level=p.congestion_level,
                simulated_congestion_score=sim_score,
                simulated_congestion_level=_score_to_level(sim_score),
                current_avg_speed_kmh=_score_to_speed(p.congestion_score),
                simulated_avg_speed_kmh=_score_to_speed(sim_score),
            )
        )

    return results


def summarize_simulation(results: list[RoadSimulationResult]) -> dict:
    """Rolls up per-road results into the kind of summary numbers
    your dashboard's What-If panel wants to show (congestion %, avg speed)."""
    if not results:
        return {}

    avg_current = round(sum(r.current_congestion_score for r in results) / len(results) * 100, 1)
    avg_simulated = round(sum(r.simulated_congestion_score for r in results) / len(results) * 100, 1)

    avg_current_speed = round(sum(r.current_avg_speed_kmh for r in results) / len(results), 1)
    avg_simulated_speed = round(sum(r.simulated_avg_speed_kmh for r in results) / len(results), 1)

    return {
        "current_congestion_pct": avg_current,
        "simulated_congestion_pct": avg_simulated,
        "congestion_change_pct": round(avg_simulated - avg_current, 1),
        "current_avg_speed_kmh": avg_current_speed,
        "simulated_avg_speed_kmh": avg_simulated_speed,
    }
