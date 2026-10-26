"""Reference data: tracked Indian cities with state and coordinates.

Coordinates drive the Open-Meteo lookup; state is the health-aggregation key.
Extend this list to widen coverage - everything downstream is data-driven.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class City:
    name: str
    state: str
    lat: float
    lon: float


CITIES: list[City] = [
    City("Delhi", "Delhi", 28.6139, 77.2090),
    City("Mumbai", "Maharashtra", 19.0760, 72.8777),
    City("Pune", "Maharashtra", 18.5204, 73.8567),
    City("Kolkata", "West Bengal", 22.5726, 88.3639),
    City("Chennai", "Tamil Nadu", 13.0827, 80.2707),
    City("Bengaluru", "Karnataka", 12.9716, 77.5946),
    City("Hyderabad", "Telangana", 17.3850, 78.4867),
    City("Kanpur", "Uttar Pradesh", 26.4499, 80.3319),
    City("Lucknow", "Uttar Pradesh", 26.8467, 80.9462),
    City("Ahmedabad", "Gujarat", 23.0225, 72.5714),
    City("Patna", "Bihar", 25.5941, 85.1376),
    City("Jaipur", "Rajasthan", 26.9124, 75.7873),
    City("Srinagar", "Jammu and Kashmir", 34.0837, 74.7973),
    City("Jammu", "Jammu and Kashmir", 32.7266, 74.8570),
]

STATES: list[str] = sorted({c.state for c in CITIES})


def cities_for_state(state: str) -> list[City]:
    return [c for c in CITIES if c.state == state]
