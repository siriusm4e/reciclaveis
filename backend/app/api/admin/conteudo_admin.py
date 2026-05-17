"""Backoffice — ConteudoEducativo + disparo de comunicação segmentada."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_perfil_interno
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.usuario import Usuario
from app.repositories.conteudo import ConteudoEducativoRepository
from app.schemas.conteudo import (
    ComunicacaoDispararRequest,
    ConteudoEducativoCreate,
    ConteudoEducativoRead,
    ConteudoEducativoUpdate,
)
from app.services.conteudo_service import ConteudoService
from app.services.notificacao_service import NotificacaoService
from app.utils.audit import gravar_auditoria

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:conteudo"],
    dependencies=[Depends(require_perfil_interno("superadmin", "moderador_conteudo", "gestor_institucional"))],
)


@router.post(
    "/conteudo/",
    response_model=ConteudoEducativoRead,
    status_code=status.HTTP_201_CREATED,
)
async def criar(
    payload: ConteudoEducativoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = ConteudoService(db)
    obj = await svc.criar(**payload.model_dump())
    await db.commit()
    await db.refresh(obj)
    return obj


@router.patch("/conteudo/{conteudo_id}", response_model=ConteudoEducativoRead)
async def atualizar(
    conteudo_id: UUID,
    payload: ConteudoEducativoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = ConteudoEducativoRepository(db)
    obj = await repo.get(conteudo_id)
    if obj is None:
        raise NotFoundError("Conteúdo não encontrado")
    svc = ConteudoService(db)
    obj = await svc.atualizar(obj, **payload.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(obj)
    return obj


@router.post("/comunicacao/disparar", response_model=dict)
async def disparar(
    payload: ComunicacaoDispararRequest,
    request: Request,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = NotificacaoService(db)
    res = svc.disparar_segmentado  # bound coroutine
    out = await res(
        finalidade=payload.finalidade,
        titulo=payload.titulo,
        corpo=payload.corpo,
        segmentacao=payload.segmentacao,
    )
    await gravar_auditoria(
        db,
        acao=f"comunicacao.disparar.{payload.finalidade}",
        recurso_tipo="comunicacao",
        payload={"finalidade": payload.finalidade, "resultado": out, "titulo": payload.titulo},
        admin_id=current_user.id,
        request=request,
    )
    await db.commit()
    return out
