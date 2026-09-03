"""
ATLAS — Road Network

Aligned with Person A's real monitored segments (from trafficFeed.js):
SEG-101 through SEG-105. This replaces the earlier placeholder R001-R010
network so both halves of the system describe the same city.
"""

# road_id -> list of directly connected road_ids
ROAD_GRAPH: dict[str, list[str]] = {
    "SEG-101": ["SEG-102", "SEG-103"],   # Central Ave & 5th St
    "SEG-102": ["SEG-101", "SEG-104"],   # North Highway Junction 4
    "SEG-103": ["SEG-101", "SEG-105"],   # East Commercial Blvd
    "SEG-104": ["SEG-102", "SEG-105"],   # West Bypass Interchange
    "SEG-105": ["SEG-103", "SEG-104"],   # South Medical Center Way
}

# Human-readable names, matching Person A's trafficFeed.js
ROAD_NAMES: dict[str, str] = {
    "SEG-101": "Central Ave & 5th St",
    "SEG-102": "North Highway Junction 4",
    "SEG-103": "East Commercial Blvd",
    "SEG-104": "West Bypass Interchange",
    "SEG-105": "South Medical Center Way",
}

# Rough coordinates for each segment, for dashboard mapping
ROAD_COORDS: dict[str, dict] = {
    "SEG-101": {"lat": 12.9716, "lng": 79.1590},
    "SEG-102": {"lat": 12.9755, "lng": 79.1630},
    "SEG-103": {"lat": 12.9700, "lng": 79.1650},
    "SEG-104": {"lat": 12.9740, "lng": 79.1690},
    "SEG-105": {"lat": 12.9680, "lng": 79.1620},
}


def all_road_ids() -> list[str]:
    return list(ROAD_GRAPH.keys())


def neighbors(road_id: str) -> list[str]:
    return ROAD_GRAPH.get(road_id, [])
