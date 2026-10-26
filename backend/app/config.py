"""Application settings, loaded once from the environment / .env file.

Keeping configuration in a single typed object (rather than scattered module
globals) makes the app easy to test and to reconfigure per environment.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (no external dependency)."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    db_path: Path = BACKEND_DIR / "data" / "tracker.db"
    # OpenAQ key: the .env uses `openAq`; also accept OPENAQ_API_KEY.
    openaq_api_key: str = field(
        default_factory=lambda: os.environ.get("openAq") or os.environ.get("OPENAQ_API_KEY", "")
    )
    openaq_base_url: str = "https://api.openaq.org/v3"
    open_meteo_url: str = "https://air-quality-api.open-meteo.com/v1/air-quality"
    cors_origins: tuple[str, ...] = ("*",)
    default_window_days: int = 540
    request_timeout: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
