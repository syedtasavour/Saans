FROM python:3.11-slim

WORKDIR /app

# cron runs the scheduled data refresh inside the container
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts
COPY docker-entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Refresh current air quality every day at 02:00 (Open-Meteo, no key needed).
RUN echo "0 2 * * * cd /app && /usr/local/bin/python -m scripts.ingest_air >> /var/log/ingest.log 2>&1" > /etc/cron.d/saans \
    && chmod 0644 /etc/cron.d/saans \
    && crontab /etc/cron.d/saans \
    && touch /var/log/ingest.log

ENV PYTHONUNBUFFERED=1
EXPOSE 8077
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
