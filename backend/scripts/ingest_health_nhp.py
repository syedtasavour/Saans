"""Load REAL state-wise Acute Respiratory Infection data from the National
Health Profile 2021 (CBHI, Ministry of Health & Family Welfare, Govt of India).

Tables 3.1.9(A) and 3.1.9(B): "State/UT wise Cases and Deaths due to Acute
Respiratory Infection in India" for 2019 and 2020
(ICD-10 J00-J06, J10, J11, J20-J22). Figures are the official totals
transcribed verbatim from the report - nothing is estimated or synthesised.

Jammu and Kashmir = Jammu Div. + Kashmir Div. (summed, as the report lists them
separately). Only the states this app shows air quality for are loaded here;
extend AR_* dicts to add more.

Run from backend/:  python -m scripts.ingest_health_nhp
Source PDF: National Health Profile 2021, pp. 170-171.
"""
from __future__ import annotations

from app.constants import CATEGORY_ARI
from app.database import get_connection, init_db

SOURCE = "National Health Profile 2021 (CBHI, MoHFW) - tables 3.1.9(A/B)"

# state -> {year: (cases, deaths)}  - verbatim from NHP 2021.
NHP_ARI = {
    "Delhi":             {2019: (279423, 359),   2020: (117579, 490)},
    "Maharashtra":       {2019: (143897, 0),     2020: (776078, 0)},
    "West Bengal":       {2019: (4149377, 884),  2020: (2587667, 661)},
    "Tamil Nadu":        {2019: (1998158, 61),   2020: (1458461, 132)},
    "Karnataka":         {2019: (2453026, 104),  2020: (1436167, 166)},
    "Telangana":         {2019: (679097, 3),     2020: (626878, 8)},
    "Uttar Pradesh":     {2019: (2942215, 575),  2020: (1004936, 236)},
    "Gujarat":           {2019: (2315080, 0),    2020: (1513206, 1338)},
    "Bihar":             {2019: (783788, 14),    2020: (157868, 0)},
    "Rajasthan":         {2019: (5346060, 48),   2020: (3643201, 20)},
    # J&K = Jammu Div. (249995/0, 139363/0) + Kashmir Div. (696335/0, 519148/0)
    "Jammu and Kashmir": {2019: (946330, 0),     2020: (658511, 0)},
}


def rows():
    for state, by_year in NHP_ARI.items():
        for year, (cases, deaths) in by_year.items():
            yield ("year", f"{year}-01-01", state, CATEGORY_ARI, cases, deaths, SOURCE)


def run():
    init_db()
    data = list(rows())
    with get_connection() as conn:
        conn.executemany(
            "INSERT OR REPLACE INTO health_case "
            "(period_type, period_start, state, category, cases, deaths, source) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            data,
        )
        conn.commit()
    print(f"Loaded {len(data)} real NHP ARI rows ({len(NHP_ARI)} states × 2 years).")


if __name__ == "__main__":
    run()
