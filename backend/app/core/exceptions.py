"""Exceções de domínio + handlers globais.

Hierarquia única (DomainError) para que o handler global mapeie consistente
o status HTTP. Erros 4xx têm `code` e `message` traduzidos para o frontend.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

import structlog

log = structlog.get_logger(__name__)


class DomainError(Exception):
    """Base de erros de domínio."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "domain_error"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ConflictError(DomainError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


class UnauthorizedError(DomainError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"


class ForbiddenError(DomainError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "forbidden"


class ValidationDomainError(DomainError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "validation_error"


class RateLimitError(DomainError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "rate_limited"


# === Erros específicos de regra de negócio (subset, mais surgem nos serviços) ===

class DocumentoVencidoError(ForbiddenError):
    code = "documento_vencido"


class DocumentoFaltandoError(ForbiddenError):
    code = "documento_faltando"


class LimitePublicacoesAtingidoError(ForbiddenError):
    code = "limite_publicacoes_atingido"


class CoberturaInsuficienteError(DomainError):
    code = "cobertura_insuficiente"


class VinculoDetectadoError(ForbiddenError):
    code = "vinculo_detectado"


class TipoContaImutavelError(ConflictError):
    code = "tipo_conta_imutavel"


class AssinaturaPausadaError(ForbiddenError):
    code = "assinatura_pausada"


class LocalizacaoExataNaoAutorizadaError(ForbiddenError):
    code = "localizacao_exata_nao_autorizada"


# === Handlers ===

def _payload(*, code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": details or {}}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        log.warning("domain_error", code=exc.code, message=exc.message, details=exc.details)
        return JSONResponse(
            status_code=exc.status_code,
            content=_payload(code=exc.code, message=exc.message, details=exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_payload(
                code="validation_error",
                message="Dados inválidos",
                details={"errors": jsonable_encoder(exc.errors())},
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_payload(
                code=f"http_{exc.status_code}",
                message=str(exc.detail),
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled_exception", error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_payload(code="internal_error", message="Erro interno do servidor"),
        )
