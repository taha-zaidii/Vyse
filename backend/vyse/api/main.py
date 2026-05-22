"""FastAPI entrypoint.

In dev (`uvicorn vyse.api.main:app`) the API runs standalone against the SQLite
DB. In `__main__.py` it boots alongside the agents under the orchestrator.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from vyse.api.routes import analytics, incidents, stream
from vyse.api.routes import config as config_routes
from vyse.core.config import get_settings
from vyse.core.logging import configure_logging
from vyse.db.session import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Vyse API",
        version="0.1.0",
        description="Real-Time AI Workplace Safety Intelligence",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.env == "dev" else [],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(incidents.router, prefix="/api/v1")
    app.include_router(analytics.router, prefix="/api/v1")
    app.include_router(config_routes.router, prefix="/api/v1")
    app.include_router(stream.router)

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "service": "vyse", "version": "0.1.0"}

    @app.get("/metrics")
    async def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    return app


app = create_app()
