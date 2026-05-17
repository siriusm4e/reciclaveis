"""Backoffice — Perfis Internos + AuditLog + Configurações administráveis."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_perfil_interno
from app.core.exceptions import NotFoundError
from app.core.redis_client import get_redis_cache
from app.db.session import get_db
from app.models.perfil_interno import PerfilInterno
from app.models.usuario import Usuario
from app.repositories.moderacao import AuditLogRepository, PerfilInternoRepository
from app.schemas.common import OkResponse
from app.schemas.moderacao import (
    AuditLogRead,
    LimiarCoberturaUpdate,
    PerfilInternoCreate,
    PerfilInternoRead,
    PrazoOportunidadePublicaUpdate,
)
from app.utils.audit import gravar_auditoria

router = APIRouter(prefix="/api/admin", tags=["admin:backoffice"])


# === Perfis internos — apenas superadmin ===

@router.post(
    "/perfis-internos/",
    response_model=PerfilInternoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_perfil_interno("superadmin"))],
)
async def criar_perfil(
    payload: PerfilInternoCreate,
    request: Request,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    p = PerfilInterno(**payload.model_dump())
    db.add(p)
    await gravar_auditoria(
        db,
        acao="perfil_interno.criar",
        recurso_tipo="perfil_interno",
        recurso_id=p.id,
        payload={"usuario_id": str(payload.usuario_id), "tipo": payload.tipo.value},
        admin_id=current_user.id,
        request=request,
    )
    await db.commit()
    await db.refresh(p)
    return p


@router.get(
    "/perfis-internos/",
    response_model=list[PerfilInternoRead],
    dependencies=[Depends(require_perfil_interno("superadmin"))],
)
async def listar_perfis(db: Annotated[AsyncSession, Depends(get_db)]):
    return await PerfilInternoRepository(db).list(limit=200)


# === AuditLog — todos os perfis (filtrado por escopo) ===

@router.get(
    "/audit-log/",
    response_model=list[AuditLogRead],
    dependencies=[
        Depends(
            require_perfil_interno(
                "superadmin",
                "operador_atendimento",
                "moderador_conteudo",
                "gestor_comercial",
                "gestor_institucional",
            )
        )
    ],
)
async def listar_audit(
    db: Annotated[AsyncSession, Depends(get_db)],
    recurso_tipo: str | None = Query(default=None),
    recurso_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    return await AuditLogRepository(db).listar(
        recurso_tipo=recurso_tipo,
        recurso_id=recurso_id,
        limit=page_size,
        offset=(page - 1) * page_size,
    )


# === Configurações dinâmicas ===

@router.patch(
    "/config/limiar-cobertura",
    response_model=OkResponse,
    dependencies=[Depends(require_perfil_interno("superadmin", "gestor_comercial"))],
)
async def set_limiar_cobertura(
    payload: LimiarCoberturaUpdate,
    request: Request,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Atualização em runtime via Redis (lido pelo Service em vez de settings)."""
    cache = get_redis_cache()
    await cache.set("config:alerta_pago:cobertura_minima", str(payload.valor))
    await gravar_auditoria(
        db,
        acao="config.limiar_cobertura",
        recurso_tipo="config",
        payload={"valor": payload.valor},
        admin_id=current_user.id,
        request=request,
    )
    await db.commit()
    return OkResponse(ok=True)


@router.patch(
    "/config/prazo-oportunidade-publica",
    response_model=OkResponse,
    dependencies=[Depends(require_perfil_interno("superadmin", "gestor_institucional"))],
)
async def set_prazo_oportunidade(
    payload: PrazoOportunidadePublicaUpdate,
    request: Request,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    cache = get_redis_cache()
    await cache.set("config:oportunidade:prazo_min_dias_uteis", str(payload.dias_uteis))
    await gravar_auditoria(
        db,
        acao="config.prazo_oportunidade_publica",
        recurso_tipo="config",
        payload={"dias_uteis": payload.dias_uteis},
        admin_id=current_user.id,
        request=request,
    )
    await db.commit()
    return OkResponse(ok=True)


_ = NotFoundError
