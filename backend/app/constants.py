"""Domain constants shared across the app."""
from __future__ import annotations

# Pollutant codes we store/serve, and the Open-Meteo field each maps from.
OPEN_METEO_FIELDS: dict[str, str] = {
    "pm2_5": "pm25",
    "pm10": "pm10",
    "nitrogen_dioxide": "no2",
    "sulphur_dioxide": "so2",
    "ozone": "o3",
    "carbon_monoxide": "co",
}

POLLUTANTS: list[str] = list(OPEN_METEO_FIELDS.values())

# Respiratory categories used in the health table.
CATEGORY_ARI = "Acute Respiratory Infection (ARI)"
CATEGORY_SEVERE = "Severe / oxygen-support"
HEALTH_CATEGORIES = [CATEGORY_ARI, CATEGORY_SEVERE]

# Granularities the UI offers. 'day' intentionally has no health data.
GRANULARITIES = ["day", "week", "month", "year"]
HEALTH_PERIODS = {"week", "month", "year"}

HEALTH_DISCLAIMER = (
    "Every figure here is real official data. Respiratory cases: National Health "
    "Profile (CBHI, MoHFW) state-wise Acute Respiratory Infection cases and deaths "
    "for 2019 and 2020. Air quality: annual city means from the WHO Ambient Air "
    "Quality Database for those years, plus recent daily data (Open-Meteo) and live "
    "CPCB station readings (OpenAQ). India publishes no daily respiratory-case data, "
    "so the case correlation is yearly; recent years show air quality only."
)
