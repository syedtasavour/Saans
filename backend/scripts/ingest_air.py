"""Ingest daily air-quality history from Open-Meteo into SQLite.

Open-Meteo returns hourly pollutant concentrations (keyless, long history, no
rate limits). We average them to one value per day per pollutant - this is the
source of truth for the chart at every granularity.

Run from the backend/ directory:
    python -m scripts.ingest_air                # default window (settings)
    python -m scripts.ingest_air 2024-01-01     # explicit start date
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, timedelta

from app.config import get_settings
from app.constants import OPEN_METEO_FIELDS
from app.data.cities import CITIES
from app.database import get_connection, init_db


def fetch_city(lat: float, lon: float, start: str, end: str) -> dict:
    settings = get_settings()
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(OPEN_METEO_FIELDS),
        "start_date": start,
        "end_date": end,
        "timezone": "Asia/Kolkata",
    }
    url = f"{settings.open_meteo_url}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=settings.request_timeout) as resp:
        return json.loads(resp.read().decode())


def daily_means(hourly: dict) -> dict[str, dict[str, float]]:
    """Collapse hourly arrays into {pollutant_code: {day: mean}}."""
    times = hourly.get("time", [])
    result: dict[str, dict[str, float]] = {}
    for field, code in OPEN_METEO_FIELDS.items():
        buckets: dict[str, list[float]] = defaultdict(list)
        for timestamp, value in zip(times, hourly.get(field) or []):
            if value is None:
                continue
            buckets[timestamp[:10]].append(value)  # YYYY-MM-DD
        result[code] = {
            day: round(sum(values) / len(values), 2)
            for day, values in buckets.items()
            if values
        }
    return result


def run(start: str) -> None:
    init_db()
    end = date.today().isoformat()
    total = 0
    with get_connection() as conn:
        for city in CITIES:
            try:
                payload = fetch_city(city.lat, city.lon, start, end)
            except Exception as exc:  # noqa: BLE001
                print(f"  ! {city.name}: {exc}")
                continue
            rows = [
                (day, city.name, city.state, code, value)
                for code, per_day in daily_means(payload.get("hourly", {})).items()
                for day, value in per_day.items()
            ]
            conn.executemany(
                "INSERT OR REPLACE INTO air_quality "
                "(date, city, state, pollutant, value) VALUES (?, ?, ?, ?, ?)",
                rows,
            )
            conn.commit()
            total += len(rows)
            print(f"  + {city.name:<10} {len(rows):>6} rows")
    print(f"Done. {total} air-quality rows ingested ({start} -> {end}).")


def main() -> None:
    settings = get_settings()
    start = (
        sys.argv[1]
        if len(sys.argv) > 1
        else (date.today() - timedelta(days=settings.default_window_days)).isoformat()
    )
    run(start)


if __name__ == "__main__":
    main()
