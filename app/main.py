"""LeafLens API - FastAPI application factory."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import getLogger

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import get_settings
from app.db.engine import engine, init_db
from app.logging_config import setup_logging
from app.sentry import init_sentry

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Startup and shutdown lifecycle."""
    settings = get_settings()
    setup_logging(debug=settings.debug)
    logger.info("LeafLens API starting up")
    init_sentry(settings.sentry_dsn, "development" if settings.debug else "production")
    await init_db()
    yield
    # Shutdown
    from app.clients.thingsboard import _tb_client

    if _tb_client:
        await _tb_client.close()
    await engine.dispose()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title="LeafLens API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Middleware (last added = first executed)
    from app.middleware import RateLimitMiddleware, RequestIDMiddleware

    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Error handlers
    from app.utils.errors import LeafLensError, leaflens_error_handler

    app.add_exception_handler(LeafLensError, leaflens_error_handler)

    # Routers
    from app.routers import devices, health, rpc, telemetry, ws

    app.include_router(devices.router)
    app.include_router(telemetry.router)
    app.include_router(health.router)
    app.include_router(rpc.router)
    app.include_router(ws.router)

    # Health probes (no auth, no rate limit)

    @app.get("/api/v1/health")
    async def liveness() -> dict[str, str]:
        return {"status": "ok", "version": "1.0.0"}

    @app.get("/api/v1/ready")
    async def readiness() -> JSONResponse:
        checks: dict[str, bool] = {"database": False, "thingsboard": False}
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            checks["database"] = True
        except Exception:
            logger.warning("Database health check failed")
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{settings.tb_url}/api/auth/user")
                checks["thingsboard"] = resp.status_code in (200, 401)
        except Exception:
            logger.warning("ThingsBoard health check failed")

        all_ok = all(checks.values())
        return JSONResponse(
            status_code=200 if all_ok else 503,
            content={"status": "ready" if all_ok else "degraded", "checks": checks},
        )

    return app


app = create_app()
