"""Rotas — Créditos (saldo projetado, histórico, compra de pacote)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, require_papel_interno
from app.db.session import get_db
from app.models.conta import Conta
from app.repositories.creditos import (
    PacoteCreditoRepository,
    TransacaoCreditoRepository,
)
from app.schemas.creditos import (
    CompraPacoteRequest,
    PacoteCreditoRead,
    SaldoCreditos,
    TransacaoCreditoRead,
)
from app.services.creditos_service import CreditosService

router = APIRouter(prefix="/api/creditos", tags=["creditos"])


@router.get("/saldo", response_model=SaldoCreditos)
async def saldo(
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = CreditosService(db)
    return SaldoCreditos(conta_id=conta.id, saldo=await svc.saldo(conta.id))


@router.get("/transacoes", response_model=list[TransacaoCreditoRead])
async def transacoes(
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    return await TransacaoCreditoRepository(db).historico(
        conta.id, limit=page_size, offset=(page - 1) * page_size
    )


@router.get("/pacotes", response_model=list[PacoteCreditoRead])
async def listar_pacotes(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await PacoteCreditoRepository(db).listar_ativos()


@router.post(
    "/comprar",
    response_model=TransacaoCreditoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def comprar(
    payload: CompraPacoteRequest,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = CreditosService(db)
    t = await svc.comprar_pacote(conta_id=conta.id, pacote_id=payload.pacote_id)
    await db.commit()
    await db.refresh(t)
    return t
