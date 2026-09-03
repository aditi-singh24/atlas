"""
ATLAS — Prediction Adapter

Person A's live API (Node.js/Express, GET /api/predictions) returns a
DIFFERENT shape than the schema originally agreed on. Rather than asking
either of you to rewrite already-working code, this adapter translates
Person A's real output into Person B's PredictionOutput at the boundary.
This is the ONLY file that needs to know about both shapes.

Person A's actual fields  →  Person B's PredictionOutput fields
---------------------------------------------------------------
segmentId                →  road_id                (kept as-is, e.g. "SEG-101")
timestamp                →  timestamp               (already ISO 8601, kept as-is)
alertLevel                →  congestion_level        (values already match: LOW/MEDIUM/HIGH/SEVERE)
predictedCongestion (0-100) → congestion_score (0.0-1.0)   (divided by 100)
predictedInMinutes (number) → predicted_for (string)        ("next_18_min")
factors.historyScore      →  factors.history_weight
factors.weatherScore      →  factors.weather_weight
factors.eventScore        →  factors.event_weight
"""

from app.schema import PredictionOutput, CongestionLevel, Factors


def adapt_prediction(raw: dict) -> PredictionOutput:
    """Converts one raw prediction object from Person A's API into the
    shared PredictionOutput shape Person B's engine expects."""

    factors = raw.get("factors", {})

    return PredictionOutput(
        road_id=raw["segmentId"],
        timestamp=raw["timestamp"],
        congestion_level=CongestionLevel(raw["alertLevel"]),
        congestion_score=round(raw["predictedCongestion"] / 100, 2),
        predicted_for=f"next_{raw.get('predictedInMinutes', 15)}_min",
        factors=Factors(
            history_weight=factors.get("historyScore", 0.33),
            weather_weight=factors.get("weatherScore", 0.33),
            event_weight=factors.get("eventScore", 0.33),
        ),
    )


def adapt_predictions(raw_list: list[dict]) -> list[PredictionOutput]:
    """Converts Person A's full /api/predictions response (a list) into
    a list of PredictionOutput objects."""
    return [adapt_prediction(item) for item in raw_list]
