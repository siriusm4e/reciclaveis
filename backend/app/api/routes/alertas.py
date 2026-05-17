"""Rotas — AssinaturaAlerta (gratuita, filtros de push)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, require_papel_interno
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.assinatura_alerta import AssinaturaAlerta
from app.models.conta import Conta
from app.repositories.marketplace import AssinaturaAlertaRepository
from app.schemas.marketplace import (
    AssinaturaAlertaCreate,
    AssinaturaAlertaRead,
    AssinaturaAlertaUpdate,
)

router = APIRouter(prefix="/api/alertas-assinatura", tags=["alertas"])


@router.get("/", response_model=list[AssinaturaAlertaRead])
async def listar(
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await AssinaturaAlertaRepository(db).listar_da_conta(conta.id)


@router.post(
    "/",
    response_model=AssinaturaAlertaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def criar(
    payload: AssinaturaAlertaCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    obj = AssinaturaAlerta(
        conta_id=conta.id,
        papel_id=payload.papel_id,
        categoria_id=payload.categoria_id,
        subcategoria_ids=payload.subcategoria_ids,
        raio_km=payload.raio_km,
        preco_min=payload.preco_min,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.patch(
    "/{alerta_id}",
    response_model=AssinaturaAlertaRead,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def atualizar(
    alerta_id: UUID,
    payload: AssinaturaAlertaUpdate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = AssinaturaAlertaRepository(db)
    obj = await repo.get(alerta_id)
    if obj is None:
        raise NotFoundError("Alerta não encontrado")
    if obj.conta_id != conta.id:
        raise ForbiddenError("Alerta pertence a outra Conta")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj
