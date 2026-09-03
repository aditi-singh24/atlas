"""
ATLAS — Shared Data Contract
Both Person A (Prediction) and Person B (Traffic Control) import this file
so the JSON shapes passed between the two systems never drift apart.

DO NOT rename or remove fields here without telling your teammate.
Adding new OPTIONAL fields is fine.
"""

from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel


class CongestionLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    SEVERE = "SEVERE"


class SignalState(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    GREEN_EXTENDED = "GREEN_EXTENDED"


class Factors(BaseModel):
    history_weight: float
    weather_weight: float
    event_weight: float


class PredictionOutput(BaseModel):
    """Produced by Person A's Prediction Engine."""
    road_id: str
    timestamp: str  # ISO 8601
    congestion_level: CongestionLevel
    congestion_score: float  # 0.0 - 1.0
    predicted_for: str  # e.g. "next_15_min"
    factors: Factors


class ControlOutput(BaseModel):
    """Produced by Person B's Traffic Control engine."""
    road_id: str
    signal_state: SignalState
    recommended_route: List[str]
    emergency_priority: bool
    reason: str


class EmergencyVehicle(BaseModel):
    vehicle_id: str
    current_road: str
    destination_road: str
    priority: bool
