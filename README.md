<div align="center">

# Saans - India Air Quality & Respiratory Burden

**Does worse air mean more respiratory illness? Saans pairs real air-quality data
with real government respiratory-case data for Indian states, side by side.**

*Saans* (साँस) means "breath". Every number in this app is real official data.
Nothing is estimated, synthesised, or faked.

[![Star this repo](https://img.shields.io/badge/Star_this_repo-GitHub-181717?logo=github)](https://github.com/syedtasavour/Saans)

</div>

---

## What it shows

For a state and year, Saans lines up:

- **Air quality** (PM2.5 / PM10 / NO2), and
- **Acute Respiratory Infection (ARI) cases and deaths**

so you can read, for example: *West Bengal, 2019: PM2.5 68 ug/m3, 4,149,377 ARI
cases, 884 deaths.* Plus a live reading from the nearest real CPCB station.

## The data (all real, all official)

| Layer | Source | Coverage | How |
|-------|--------|----------|-----|
| Respiratory cases | **National Health Profile 2021**, CBHI / MoHFW (tables 3.1.9 A/B) | state-wise ARI cases + deaths, **2019 & 2020** (ICD-10 J00-J22) | transcribed from the official PDF |
| Air quality (those years) | **WHO Ambient Air Quality Database** v6.1 (2024) | annual city mean PM2.5 / PM10 / NO2, 2019 & 2020 | downloaded .xlsx |
| Air quality (recent) | **Open-Meteo** (CAMS model) | daily, 2024-present | API |
| Live station | **OpenAQ** (real CPCB / state-board monitors) | latest reading | API (key) |

### Honest limits
India publishes **no daily** respiratory-case data, and no respiratory *outbreak*
data (IDSP outbreaks are waterborne/vector-borne only - verified). So the
case-vs-air correlation is **yearly (2019 & 2020)**, the two years where real
state-wise cases (NHP) and real city air quality (WHO) both exist. Recent years
show air quality only, because there are no case numbers to honestly pair with them.

## How it works

```
ingest_health_nhp  (NHP 2021 ARI, 2019-2020)      ┐
ingest_air_who     (WHO annual city PM2.5, 2019-20)├──►  SQLite  ──►  FastAPI  ──►  React + Mantine
ingest_air         (Open-Meteo daily, recent)     ┘      (air +        /api/*         year view pairs
                                                          health)                     air vs cases
```

The API averages a state's cities per period and rolls days up into
day/week/month/year. The frontend defaults to the **year** view so the real
2019/2020 correlation is visible on load.

## Run it (Docker)

```bash
# OpenAQ key for live stations: create .env next to docker-compose.yml
echo "openAq=YOUR_OPENAQ_KEY" > .env

docker compose up --build
# open http://localhost:5173
```

Two containers: `backend` (FastAPI + SQLite + a daily cron that refreshes current
air quality) and `frontend` (nginx serving the built app, proxying `/api`). On
first start the backend loads the NHP + WHO + Open-Meteo data into a persisted
volume automatically.

## Run it (without Docker)

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.ingest_health_nhp     # real NHP ARI (2019-2020)
python -m scripts.ingest_air_who        # real WHO annual air quality (2019-2020)
python -m scripts.ingest_air            # recent daily air quality
uvicorn app.main:app --reload --port 8077

# Frontend (separate terminal)
cd frontend && npm install && npm run dev   # http://localhost:5173
```

## Architecture

```
saans/
├── docker-compose.yml        two services, one persisted volume
├── backend/                  FastAPI + SQLite (stdlib sqlite3)
│   ├── Dockerfile            + cron for the daily refresh
│   ├── docker-entrypoint.sh  seeds data on first run, then serves
│   ├── app/
│   │   ├── main.py  config.py  constants.py  database.py  schemas.py
│   │   ├── api/routes.py           thin HTTP layer
│   │   ├── services/
│   │   │   ├── aggregation.py      bucketing, overview query, meta
│   │   │   └── openaq.py           live-station client
│   │   └── data/cities.py          tracked cities -> state + coordinates
│   └── scripts/
│       ├── ingest_health_nhp.py    real NHP respiratory data
│       ├── ingest_air_who.py       real WHO annual air quality
│       └── ingest_air.py           recent daily air quality
└── frontend/                 React + Vite + Mantine + @mantine/charts
    └── src/  App.jsx  theme.js  api.js  components/
```

## API

| Endpoint | Description |
|----------|-------------|
| `GET /api/states` | states with coverage |
| `GET /api/meta` | available date range + pollutants |
| `GET /api/overview?state=&granularity=day\|week\|month\|year&from=&to=` | air quality + ARI cases |
| `GET /api/live?state=` | nearest real station's latest reading |
| `GET /api/health-note` | data provenance note |

Interactive docs: `http://localhost:8077/docs`.

## Extending it

- **More states / cities:** add a `City(...)` row to `backend/app/data/cities.py`.
- **More years:** add the state-wise ARI numbers from another National Health
  Profile edition to `ingest_health_nhp.py` (WHO data already covers 2010-2022).

---

<div align="center">

Built by **[Syed Tasavour](https://syedtasavour.com)**

If Saans is useful to you, please star the repo: **[github.com/syedtasavour/Saans](https://github.com/syedtasavour/Saans)**

Licensed under the [MIT License](LICENSE).

</div>
