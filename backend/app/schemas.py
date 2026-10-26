"""Pydantic response models - the API's public contract.

Typing the responses gives us validation, OpenAPI docs for free, and a stable
shape the frontend can rely on. We use `Optional[...]` (not `X | None`) so the
models evaluate cleanly on Python 3.9.
"""
from typing import List, Optional

from pydantic import BaseModel


class StatesResponse(BaseModel):
    states: List[str]


class NoteResponse(BaseModel):
    note: str


class MetaResponse(BaseModel):
    date_min: Optional[str] = None
    date_max: Optional[str] = None
    pollutants: List[str]


class OverviewPoint(BaseModel):
    period: str
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    o3: Optional[float] = None
    co: Optional[float] = None
    ari_cases: Optional[int] = None
    ari_deaths: Optional[int] = None
    severe_cases: Optional[int] = None
    severe_deaths: Optional[int] = None
    health_source: Optional[str] = None
    health_available: bool = False


class OverviewResponse(BaseModel):
    state: str
    granularity: str
    date_from: str
    date_to: str
    pollutants: List[str]
    health_available: bool
    points: List[OverviewPoint]


class StationReading(BaseModel):
    parameter: str
    value: Optional[float] = None
    unit: Optional[str] = None
    datetime: Optional[str] = None


class LiveStation(BaseModel):
    station: Optional[str] = None
    provider: Optional[str] = None
    readings: List[StationReading] = []


class LiveResponse(BaseModel):
    city: str
    state: str
    live: Optional[LiveStation] = None
    error: Optional[str] = None
