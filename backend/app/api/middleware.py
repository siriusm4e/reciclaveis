"""Middlewares — request id, structured logging, rate limiting."""

from __future__ import annotations

import time
import uuid

import structlog
from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.core.config import settings

log = structlog.get_logger(__name__)


# === Rate limiter (slowapi) ===
# Chave por IP no rate limit público; rotas autenticadas redefinem via decorator.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_PUBLIC],
)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Injeta request_id e mede latência. Loga acesso estruturado."""

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            client=request.client.host if request.client else None,
        )
        started = time.perf_counter()
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = (time.perf_counter() - started) * 1000
            log.info(
                "request_completed",
                status=getattr(locals().get("response"), "status_code", None),
                duration_ms=round(duration_ms, 2),
            )
            structlog.contextvars.clear_contextvars()


def register_middlewares(app: FastAPI) -> None:
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(RequestContextMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_handler(_: Request, exc: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "rate_limited",
                    "message": "Limite de requisições excedido",
                    "details": {"limit": str(exc.detail)},
                }
            },
        )
