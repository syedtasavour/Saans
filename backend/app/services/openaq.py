"""OpenAQ v3 client - powers the 'nearest real government station' card.

The historical chart comes from Open-Meteo; this module grounds the app in
real CPCB monitoring data by showing the closest station's latest readings.
All network access to OpenAQ is funnelled through here.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

from app.config import get_settings


def _request(path: str, params: dict) -> dict:
    settings = get_settings()
    url = f"{settings.openaq_base_url}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"X-API-Key": settings.openaq_api_key})
    with urllib.request.urlopen(req, timeout=settings.request_timeout) as resp:
        return json.loads(resp.read().decode())


def nearest_station(lat: float, lon: float, radius_m: int = 25_000) -> dict | None:
    """Pick the *freshest* station near a point.

    OpenAQ's India feed has many stale stations, so returning the merely
    closest one can surface years-old data. We fetch several candidates in the
    radius and choose the one with the most recent last reading.
    """
    data = _request(
        "/locations",
        {
            "coordinates": f"{lat},{lon}",
            "radius": radius_m,
            "limit": 50,
        },
    )
    results = data.get("results") or []
    if not results:
        return None

    def last_seen(station: dict) -> str:
        return ((station.get("datetimeLast") or {}).get("utc")) or ""

    results.sort(key=last_seen, reverse=True)  # newest reading first
    return results[0]


# The six pollutants we display, in order, with clean labels. Stations expose
# many overlapping sensors (ppb + mass variants, meteorology); we keep exactly
# one reading per pollutant and drop the rest so the card stays legible.
_CANONICAL = [
    ("pm25", "PM2.5"),
    ("pm10", "PM10"),
    ("no2", "NO₂"),
    ("so2", "SO₂"),
    ("o3", "O₃"),
    ("co", "CO"),
]


def _canonical_code(param_name: str) -> str | None:
    name = (param_name or "").lower()
    for code, _label in _CANONICAL:
        if name.startswith(code):
            return code
    return None


def latest_readings(lat: float, lon: float) -> dict | None:
    """Closest fresh station's latest reading for each core pollutant."""
    station = nearest_station(lat, lon)
    if not station:
        return None

    sensor_meta = {
        sensor["id"]: {
            "name": (sensor.get("parameter") or {}).get("name"),
            "units": (sensor.get("parameter") or {}).get("units"),
        }
        for sensor in station.get("sensors", [])
    }

    latest = _request(f"/locations/{station['id']}/latest", {"limit": 100})

    # Pick the best reading per pollutant: prefer µg/m³ (mass) over ppb.
    best: dict[str, dict] = {}
    for row in latest.get("results", []):
        meta = sensor_meta.get(row.get("sensorsId"))
        if not meta:
            continue
        code = _canonical_code(meta["name"])
        if not code:
            continue
        unit = meta["units"] or ""
        is_mass = "g/m" in unit  # matches "µg/m³" / "ug/m3"
        if code not in best or (is_mass and not best[code]["_mass"]):
            best[code] = {
                "value": row.get("value"),
                "unit": unit,
                "datetime": (row.get("datetime") or {}).get("utc"),
                "_mass": is_mass,
            }

    readings = [
        {
            "parameter": label,
            "value": best[code]["value"],
            "unit": best[code]["unit"],
            "datetime": best[code]["datetime"],
        }
        for code, label in _CANONICAL
        if code in best
    ]

    return {
        "station": station.get("name"),
        "provider": (station.get("provider") or {}).get("name"),
        "readings": readings,
    }
