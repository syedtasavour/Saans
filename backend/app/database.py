"""SQLite access layer.

We use the stdlib `sqlite3` with a thin context-managed connection instead of
an ORM: the schema is two flat tables and the queries are simple aggregations,
so an ORM would add dependency weight without buying much. The connection
factory and schema live here so nothing else touches the driver directly.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from app.config import get_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS air_quality (
    date      TEXT    NOT NULL,          -- YYYY-MM-DD
    city      TEXT    NOT NULL,
    state     TEXT    NOT NULL,
    pollutant TEXT    NOT NULL,          -- pm25, pm10, no2, so2, o3, co
    value     REAL,
    PRIMARY KEY (date, city, pollutant)
);

CREATE TABLE IF NOT EXISTS health_case (
    period_type  TEXT    NOT NULL,       -- week | month | year
    period_start TEXT    NOT NULL,       -- YYYY-MM-DD (first day of period)
    state        TEXT    NOT NULL,
    category     TEXT    NOT NULL,
    cases        INTEGER,
    deaths       INTEGER,
    source       TEXT,
    PRIMARY KEY (period_type, period_start, state, category)
);

CREATE INDEX IF NOT EXISTS idx_aq_state_date ON air_quality (state, date);
CREATE INDEX IF NOT EXISTS idx_health_lookup ON health_case (state, period_type, period_start);
"""


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    settings = get_settings()
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        conn.commit()
