"""
ATLAS — Mock Prediction Data

Stand-in for Person A's real GET /api/predictions endpoint.
Lets you build and test Traffic Control right now, independently.

Once Person A's API is live, delete this file's usage in main.py and
call their endpoint instead (see fetch_predictions() in main.py —
that's the ONLY place you'll need to change).
"""

import random
from datetime import datetime, timezone
from app.schema import PredictionOutput, CongestionLevel, Factors
from app.network import all_road_ids


def generate_mock_predictions() -> list[PredictionOutput]:
    """Randomly generates plausible congestion predictions for every road."""
    predictions = []
    now = datetime.now(timezone.utc).isoformat()

    for road_id in all_road_ids():
        score = round(random.uniform(0.1, 0.95), 2)

        if score < 0.35:
            level = CongestionLevel.LOW
        elif score < 0.6:
            level = CongestionLevel.MEDIUM
        elif score < 0.8:
            level = CongestionLevel.HIGH
        else:
            level = CongestionLevel.SEVERE

        predictions.append(
            PredictionOutput(
                road_id=road_id,
                timestamp=now,
                congestion_level=level,
                congestion_score=score,
                predicted_for="next_15_min",
                factors=Factors(
                    history_weight=0.4,
                    weather_weight=0.3,
                    event_weight=0.3,
                ),
            )
        )
    return predictions
