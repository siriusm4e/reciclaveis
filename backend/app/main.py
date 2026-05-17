"""FastAPI app entrypoint — wiring de middlewares, exceptions, routes, OTEL."""

from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.responses import Response

from app.api.middleware import register_middlewares
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging

# Garante que models sejam registrados no Base.metadata
import app.db.base  # noqa: F401

# ===== Routers (público) =====
from app.api.routes import (
    alertas,
    analytics_publico,
    anuncios_frete,
    anuncios_maquina,
    anuncios_servico,
    anuncios_venda,
    assinaturas,
    auth as auth_routes,
    avaliacoes,
    campanhas,
    categorias,
    contas,
    conteudo_educativo,
    creditos,
    denuncias,
    dispositivos,
    documentos,
    mapa_institucional,
    membros,
    mensagens,
    negociacoes,
    ofertas_compra,
    oportunidades,
    papeis,
    pedidos_coleta,
    preferencias,
    usuarios,
)

# ===== Routers (admin / backoffice) =====
from app.api.admin import (
    analytics_admin,
    assinaturas_admin,
    campanhas_admin,
    catalogo_admin,
    contas_admin,
    conteudo_admin,
    creditos_admin,
    documentos_admin,
    moderacao_admin,
    perfis_internos_admin,
)

# ===== WebSocket =====
from app.api.ws import chat as ws_chat, notificacoes as ws_notif


log = structlog.get_logger(__name__)


def _setup_telemetry(app: FastAPI) -> None:
    """OpenTelemetry — fastapi + sqlalchemy + redis. Falha silenciosa em dev."""
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": settings.OTEL_SERVICE_NAME})
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{settings.OTEL_EXPORTER_OTLP_ENDPOINT}/v1/traces"))
        )
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app)
        SQLAlchemyInstrumentor().instrument()
        RedisInstrumentor().instrument()
        log.info("otel_enabled", endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
    except Exception as e:  # noqa: BLE001
        log.warning("otel_setup_failed", error=str(e))


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    log.info("startup", env=settings.APP_ENV, debug=settings.DEBUG)
    yield
    log.info("shutdown")


app = FastAPI(
    title="Plataforma Nacional de Resíduos",
    description="API REST + WebSocket — marketplace B2B de resíduos recicláveis",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-Id"],
)

# === Middlewares (rate limiting, request context) ===
register_middlewares(app)

# === Exception handlers ===
register_exception_handlers(app)


# === Routes públicas ===

# Identidade / auth
app.include_router(auth_routes.router)
app.include_router(usuarios.router)
app.include_router(contas.router)
app.include_router(membros.router)
app.include_router(papeis.router_papeis)
app.include_router(papeis.router_est)

# Catálogo / documentos
app.include_router(categorias.router)
app.include_router(categorias.sub_router)
app.include_router(documentos.router)

# Marketplace
app.include_router(anuncios_venda.router)
app.include_router(ofertas_compra.router)
app.include_router(anuncios_maquina.router)
app.include_router(anuncios_servico.router)
app.include_router(anuncios_frete.router)
app.include_router(alertas.router)
app.include_router(analytics_publico.router)

# Negociação
app.include_router(negociacoes.router)
app.include_router(mensagens.router)
app.include_router(avaliacoes.router)
app.include_router(oportunidades.router)

# Créditos / assinaturas
app.include_router(creditos.router)
app.include_router(assinaturas.router)

# Institucional
app.include_router(pedidos_coleta.router)
app.include_router(campanhas.router)
app.include_router(mapa_institucional.router)

# Conteúdo / preferências / dispositivos / denúncias
app.include_router(conteudo_educativo.router)
app.include_router(preferencias.router)
app.include_router(dispositivos.router)
app.include_router(denuncias.router)


# === Routes admin (backoffice) ===

app.include_router(contas_admin.router)
app.include_router(documentos_admin.router)
app.include_router(catalogo_admin.router)
app.include_router(creditos_admin.router)
app.include_router(assinaturas_admin.router)
app.include_router(moderacao_admin.router)
app.include_router(campanhas_admin.router)
app.include_router(conteudo_admin.router)
app.include_router(analytics_admin.router)
app.include_router(perfis_internos_admin.router)


# === WebSocket ===

app.include_router(ws_chat.router)
app.include_router(ws_notif.router)


# === Health / version ===

@app.get("/api/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.APP_ENV, "version": app.version}


@app.get("/api/version", tags=["meta"])
async def version_endpoint() -> dict[str, str]:
    return {"name": settings.APP_NAME, "version": app.version}


# === Prometheus /metrics protegido por X-Metrics-Token em prod ===

Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    excluded_handlers=["/api/health", "/api/version", "/metrics"],
).instrument(app)


@app.get("/metrics", include_in_schema=False)
async def metrics(
    x_metrics_token: str | None = Header(default=None, alias="X-Metrics-Token"),
) -> Response:
    if settings.is_production and x_metrics_token != settings.METRICS_TOKEN:
        raise HTTPException(status_code=403, detail="forbidden")
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


_setup_telemetry(app)
