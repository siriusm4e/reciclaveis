"""Backoffice — Planos + cortesia de Assinatura."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_perfil_interno
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.plano import Plano
from app.models.usuario import Usuario
from app.repositories.assinatura import AssinaturaRepository, PlanoRepository
from app.schemas.creditos import AssinaturaRead, PlanoCreate, PlanoRead
from app.services.assinatura_service import AssinaturaService
from app.utils.audit import gravar_auditoria

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:assinaturas"],
    dependencies=[Depends(require_perfil_interno("superadmin", "gestor_comercial"))],
)


@router.post("/planos/", response_model=PlanoRead, status_code=status.HTTP_201_CREATED)
async def criar_plano(
    payload: PlanoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    p = Plano(**payload.model_dump())
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("/planos/", response_model=list[PlanoRead])
async def listar_planos(db: Annotated[AsyncSession, Depends(get_db)]):
    return await PlanoRepository(db).list(limit=200)


@router.post("/assinaturas/{assinatura_id}/cortesia", response_model=AssinaturaRead)
async def cortesia(
    assinatura_id: UUID,
    request: Request,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = AssinaturaRepository(db)
    a = await repo.get(assinatura_id)
    if a is None:
        raise NotFoundError("Assinatura não encontrada")
    svc = AssinaturaService(db)
    a = await svc.aplicar_cortesia(a)
    await gravar_auditoria(
        db,
        acao="assinatura.cortesia",
        recurso_tipo="assinatura",
        recurso_id=a.id,
        conta_afetada_id=a.conta_id,
        admin_id=current_user.id,
        request=request,
    )
    await db.commit()
    await db.refresh(a)
    return a
