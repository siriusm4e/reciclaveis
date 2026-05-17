"""Backoffice — Pacotes de Crédito + ajuste manual de saldo."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_perfil_interno
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.pacote_credito import PacoteCredito
from app.models.usuario import Usuario
from app.repositories.creditos import PacoteCreditoRepository
from app.schemas.creditos import (
    PacoteCreditoCreate,
    PacoteCreditoRead,
    TransacaoCreditoRead,
)
from app.services.creditos_service import CreditosService
from app.utils.audit import gravar_auditoria

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:creditos"],
    dependencies=[Depends(require_perfil_interno("superadmin", "gestor_comercial"))],
)


@router.post(
    "/pacotes-credito/", response_model=PacoteCreditoRead, status_code=status.HTTP_201_CREATED
)
async def criar_pacote(
    payload: PacoteCreditoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    p = PacoteCredito(**payload.model_dump())
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("/pacotes-credito/", response_model=list[PacoteCreditoRead])
async def listar_pacotes(db: Annotated[AsyncSession, Depends(get_db)]):
    return await PacoteCreditoRepository(db).list(limit=200)


@router.post(
    "/creditos/ajuste",
    response_model=TransacaoCreditoRead,
)
async def ajuste_admin(
    conta_id: UUID,
    valor: int,
    descricao: str,
    request: Request,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = CreditosService(db)
    t = await svc.ajuste_admin(
        conta_id=conta_id, valor=valor, descricao=descricao, admin_id=current_user.id
    )
    await gravar_auditoria(
        db,
        acao="creditos.ajuste_admin",
        recurso_tipo="conta",
        recurso_id=conta_id,
        conta_afetada_id=conta_id,
        payload={"valor": valor, "descricao": descricao},
        admin_id=current_user.id,
        request=request,
    )
    await db.commit()
    return t


_ = NotFoundError
