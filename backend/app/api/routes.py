"""HTTP routes. Thin layer: validate input, delegate to services, return schemas."""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.constants import GRANULARITIES, HEALTH_DISCLAIMER
from app.data.cities import STATES, cities_for_state
from app.schemas import (
    LiveResponse,
    MetaResponse,
    NoteResponse,
    OverviewResponse,
    StatesResponse,
)
from app.services import openaq
from app.services.aggregation import build_overview, default_window, get_meta

router = APIRouter(prefix="/api")


@router.get("/states", response_model=StatesResponse)
def get_states() -> StatesResponse:
    return StatesResponse(states=STATES)


@router.get("/health-note", response_model=NoteResponse)
def get_health_note() -> NoteResponse:
    return NoteResponse(note=HEALTH_DISCLAIMER)


@router.get("/meta", response_model=MetaResponse)
def get_metadata() -> MetaResponse:
    return MetaResponse(**get_meta())


@router.get("/overview", response_model=OverviewResponse)
def get_overview(
    state: str = Query(..., description="State to report on"),
    granularity: str = Query("month", pattern="^(day|week|month|year)$"),
    date_from: Optional[str] = Query(None, alias="from"),
    date_to: Optional[str] = Query(None, alias="to"),
) -> OverviewResponse:
    if state not in STATES:
        raise HTTPException(status_code=404, detail=f"Unknown state: {state}")
    if granularity not in GRANULARITIES:
        raise HTTPException(status_code=400, detail="Invalid granularity")

    window_from, window_to = default_window(get_settings().default_window_days)
    return OverviewResponse(
        **build_overview(
            state=state,
            granularity=granularity,
            date_from=date_from or window_from,
            date_to=date_to or window_to,
        )
    )


@router.get("/live", response_model=LiveResponse)
def get_live(state: str = Query(..., description="State to find a station in")) -> LiveResponse:
    cities = cities_for_state(state)
    if not cities:
        raise HTTPException(status_code=404, detail=f"Unknown state: {state}")
    city = cities[0]
    try:
        live = openaq.latest_readings(city.lat, city.lon)
        return LiveResponse(city=city.name, state=state, live=live)
    except Exception as exc:  # noqa: BLE001 - surface upstream errors to the client
        return LiveResponse(city=city.name, state=state, error=str(exc))
