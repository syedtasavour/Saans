"""Core query/aggregation logic for the overview endpoint.

Air quality is stored per city per day. For a state we average across its
cities per day, then roll those daily means up into the requested granularity.
Health rows are pre-aggregated per period (week/month/year) by the seed step,
so we just join them onto the matching bucket.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta

from app.constants import (
    CATEGORY_ARI,
    CATEGORY_SEVERE,
    HEALTH_PERIODS,
    POLLUTANTS,
)
from app.database import get_connection


def bucket_key(day: str, granularity: str) -> str:
    """Map a YYYY-MM-DD date to the start of its bucket for the granularity."""
    dt = datetime.strptime(day, "%Y-%m-%d").date()
    if granularity == "week":
        return (dt - timedelta(days=dt.weekday())).isoformat()  # Monday
    if granularity == "month":
        return dt.replace(day=1).isoformat()
    if granularity == "year":
        return dt.replace(month=1, day=1).isoformat()
    return day  # 'day'


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 1) if values else None


def build_overview(
    state: str,
    granularity: str,
    date_from: str,
    date_to: str,
) -> dict:
    with get_connection() as conn:
        aq_rows = conn.execute(
            "SELECT date, pollutant, AVG(value) AS v FROM air_quality "
            "WHERE state = ? AND date BETWEEN ? AND ? "
            "GROUP BY date, pollutant",
            (state, date_from, date_to),
        ).fetchall()

        health_rows = []
        if granularity in HEALTH_PERIODS:
            # A bucket's key (e.g. year -> Jan 1) can precede date_from while the
            # bucket itself overlaps the window, so lower-bound on the bucketed
            # date_from, not the raw one, to keep health aligned with air quality.
            health_from = bucket_key(date_from, granularity)
            health_rows = conn.execute(
                "SELECT period_start, category, cases, deaths, source "
                "FROM health_case "
                "WHERE state = ? AND period_type = ? "
                "AND period_start BETWEEN ? AND ?",
                (state, granularity, health_from, date_to),
            ).fetchall()

    # bucket -> pollutant -> daily means
    aq: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in aq_rows:
        aq[bucket_key(row["date"], granularity)][row["pollutant"]].append(row["v"])

    # bucket -> category -> {cases, deaths, source}
    health: dict[str, dict[str, dict]] = defaultdict(dict)
    for row in health_rows:
        health[row["period_start"]][row["category"]] = {
            "cases": row["cases"],
            "deaths": row["deaths"],
            "source": row["source"],
        }

    points = []
    for period in sorted(set(aq) | set(health)):
        point = {"period": period}
        for pollutant in POLLUTANTS:
            point[pollutant] = _mean(aq.get(period, {}).get(pollutant, []))
        hc = health.get(period, {})
        ari = hc.get(CATEGORY_ARI, {})
        severe = hc.get(CATEGORY_SEVERE, {})
        point.update(
            ari_cases=ari.get("cases"),
            ari_deaths=ari.get("deaths"),
            severe_cases=severe.get("cases"),
            severe_deaths=severe.get("deaths"),
            health_source=ari.get("source") or severe.get("source"),
            health_available=bool(hc),
        )
        points.append(point)

    return {
        "state": state,
        "granularity": granularity,
        "date_from": date_from,
        "date_to": date_to,
        "pollutants": POLLUTANTS,
        "health_available": granularity != "day",
        "points": points,
    }


def default_window(days: int) -> tuple[str, str]:
    today = date.today()
    return (today - timedelta(days=days)).isoformat(), today.isoformat()


def get_meta() -> dict:
    """Available date range + dimensions, for initialising UI pickers."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT MIN(date) AS lo, MAX(date) AS hi FROM air_quality"
        ).fetchone()
    return {
        "date_min": row["lo"],
        "date_max": row["hi"],
        "pollutants": POLLUTANTS,
    }
