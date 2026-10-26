"""Application entry point / factory.

Run with:  uvicorn app.main:app --reload
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings
from app.database import init_db


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Saans - India Air Quality and Respiratory Burden",
        description=(
            "Pairs real daily air-quality history with respiratory-case counts "
            "by Indian state, across day/week/month/year granularities."
        ),
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)

    @app.on_event("startup")
    def _startup() -> None:
        init_db()

    @app.get("/health", tags=["meta"])
    def healthcheck() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
