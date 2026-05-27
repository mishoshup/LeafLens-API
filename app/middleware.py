"""Request ID, logging, and rate limiting middleware."""

import logging
import time
import uuid
from collections import defaultdict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every request for tracing."""

    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:12])
        request.state.request_id = request_id

        start = time.monotonic()
        response = await call_next(request)
        duration_ms = (time.monotonic() - start) * 1000

        logging.getLogger("leaflens").info(
            "%s %s → %s (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            extra={"request_id": request_id},
        )
        response.headers["X-Request-ID"] = request_id
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory sliding window rate limiter.

    For production clusters, swap to Redis-backed (slowapi or custom).
    """

    def __init__(self, app, requests_per_minute: int = 60) -> None:
        super().__init__(app)
        self.rpm = requests_per_minute
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        # Skip health probes
        if request.url.path in ("/api/v1/health", "/api/v1/ready"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Prune old entries
        self._hits[client_ip] = [t for t in self._hits[client_ip] if now - t < 60.0]

        if len(self._hits[client_ip]) >= self.rpm:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "retry_after": 60},
                headers={"Retry-After": "60"},
            )

        self._hits[client_ip].append(now)
        return await call_next(request)
