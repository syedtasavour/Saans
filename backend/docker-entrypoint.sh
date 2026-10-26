#!/usr/bin/env sh
set -e

# 1. Load the real National Health Profile ARI data (idempotent, local, fast).
python -m scripts.ingest_health_nhp || true

# 2. Seed air quality only if the database is empty (persisted in a volume).
COUNT=$(python - <<'PY' 2>/dev/null || echo 0
from app.database import get_connection
with get_connection() as c:
    print(c.execute("SELECT COUNT(*) FROM air_quality").fetchone()[0])
PY
)
if [ "$COUNT" = "0" ]; then
    echo "Empty database - seeding air quality..."
    python -m scripts.ingest_air || true       # current daily (Open-Meteo)
    python -m scripts.ingest_air_who || true    # 2019-2020 annual (WHO), to match NHP
fi

# 3. Start cron (daily refresh) then hand off to the API server.
cron
exec uvicorn app.main:app --host 0.0.0.0 --port 8077
