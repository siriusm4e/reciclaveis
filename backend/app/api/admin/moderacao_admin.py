"""Backoffice — Moderação (fila de Denúncias + Decisões)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_perfil_interno
from app.db.session import get_db
from app.models.usuario import Usuario
from app.repositories.moderacao import DenunciaRepository
from app.schemas.moderacao import (
    DecisaoModeracaoCreate,
    DecisaoModeracaoRead,
    DenunciaRead,
)
from app.services.moderacao_service import ModeracaoService
from app.utils.audit import gravar_auditoria

router = APIRouter(
    prefix="/api/admin/denuncias",
    tags=["admin:moderacao"],
    dependencies=[Depends(require_perfil_interno("superadmin", "moderador_conteudo"))],
)


@router.get("/", response_model=list[DenunciaRead])
async def fila(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    return await DenunciaRepository(db).fila_aberta(
        limit=page_size, offset=(page - 1) * page_size
    )


@router.post("/{denuncia_id}/decidir", response_model=DecisaoModeracaoRead)
async def decidir(
    denuncia_id: UUID,
    payload: DecisaoModeracaoCreate,
    request: Request,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = ModeracaoService(db)
    dec = await svc.decidir(
        denuncia_id=denuncia_id,
        admin_id=current_user.id,
        acao=payload.acao,
        motivo=payload.motivo,
    )
    await gravar_auditoria(
        db,
        acao=f"moderacao.{payload.acao.value}",
        recurso_tipo="denuncia",
        recurso_id=denuncia_id,
        payload={"acao": payload.acao.value},
        motivo=payload.motivo,
        admin_id=current_user.id,
        request=request,
    )
    await db.commit()
    await db.refresh(dec)
    return dec
