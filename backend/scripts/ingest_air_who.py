"""Ingest REAL annual city air quality from the WHO Ambient Air Quality
Database (update 2024, v6.1) for the years the National Health Profile covers.

WHO publishes city-wide annual mean PM2.5 / PM10 / NO2, built from national
ground-station networks (CPCB in India), for 2010-2022. We take 2019 and 2020
for the tracked cities so the app can line up real air quality against the real
NHP respiratory counts for those years.

It downloads the official .xlsx, filters to India + our cities, and stores one
nominal mid-year row per city/pollutant. Values marked "NA" by WHO are skipped.

Run from backend/:  python -m scripts.ingest_air_who
Source: https://www.who.int/data/gho/data/themes/air-pollution/who-air-quality-database
"""
from __future__ import annotations

import tempfile
import urllib.request
from pathlib import Path

import openpyxl

from app.data.cities import CITIES
from app.database import get_connection, init_db

WHO_URL = (
    "https://cdn.who.int/media/docs/default-source/air-pollution-documents/"
    "air-quality-and-health/who_ambient_air_quality_database_version_2024_(v6.1).xlsx"
    "?sfvrsn=c504c0cd_3&download=true"
)
YEARS = {2019, 2020}
POLLUTANT_COLUMNS = {"pm25_concentration": "pm25", "pm10_concentration": "pm10", "no2_concentration": "no2"}

# WHO city label (lowercased, before "/IND") -> our city name
CITY_ALIASES = {"bangalore": "Bengaluru"}
CITY_BY_NAME = {c.name: c for c in CITIES}


def download(dest: Path) -> None:
    req = urllib.request.Request(WHO_URL, headers={"User-Agent": "saans-ingest"})
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
        f.write(r.read())


def match_city(label: str):
    name = (label or "").split("/")[0].strip()
    name = CITY_ALIASES.get(name.lower(), name)
    return CITY_BY_NAME.get(name)


def run() -> None:
    init_db()
    with tempfile.TemporaryDirectory() as tmp:
        xlsx = Path(tmp) / "who.xlsx"
        print("Downloading WHO Ambient Air Quality Database...")
        download(xlsx)
        wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
        ws = wb["Update 2024 (V6.1)"]
        rows = ws.iter_rows(values_only=True)
        idx = {h: i for i, h in enumerate(next(rows))}

        out = []
        for r in rows:
            if (r[idx["country_name"]] or "").strip().lower() != "india":
                continue
            if r[idx["year"]] not in YEARS:
                continue
            city = match_city(r[idx["city"]])
            if not city:
                continue
            year = r[idx["year"]]
            for col, code in POLLUTANT_COLUMNS.items():
                val = r[idx[col]]
                if isinstance(val, (int, float)):  # skip "NA" strings / blanks
                    out.append((f"{year}-07-01", city.name, city.state, code, round(float(val), 2)))

    with get_connection() as conn:
        conn.executemany(
            "INSERT OR REPLACE INTO air_quality (date, city, state, pollutant, value) "
            "VALUES (?, ?, ?, ?, ?)",
            out,
        )
        conn.commit()
    print(f"Loaded {len(out)} real WHO annual air-quality values (2019-2020).")


if __name__ == "__main__":
    run()
