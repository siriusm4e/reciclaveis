"""Rotas — Assinaturas, Planos, Faturas, Pagamentos."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, require_papel_interno
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.conta import Conta
from app.models.enums import PagamentoMetodo, PagamentoStatus, PapelTipo
from app.repositories.assinatura import (
    AssinaturaRepository,
    FaturaRepository,
    PlanoRepository,
)
from app.schemas.creditos import (
    AssinaturaCreate,
    AssinaturaRead,
    FaturaRead,
    PlanoRead,
)
from app.schemas.common import OkResponse
from app.services.assinatura_service import AssinaturaService

router = APIRouter(prefix="/api", tags=["assinaturas"])


@router.get("/planos/", response_model=list[PlanoRead])
async def listar_planos(
    db: Annotated[AsyncSession, Depends(get_db)],
    papel: PapelTipo,
):
    return await PlanoRepository(db).listar_por_papel(papel)


@router.post(
    "/assinaturas/",
    response_model=AssinaturaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin"))],
)
async def assinar(
    payload: AssinaturaCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = AssinaturaService(db)
    a = await svc.assinar(conta_id=conta.id, papel_id=payload.papel_id, plano_id=payload.plano_id)
    await db.commit()
    await db.refresh(a)
    return a


@router.get("/assinaturas/", response_model=list[AssinaturaRead])
async def listar_assinaturas(
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await AssinaturaRepository(db).listar_da_conta(conta.id)


@router.post(
    "/assinaturas/{assinatura_id}/cancelar",
    response_model=AssinaturaRead,
    dependencies=[Depends(require_papel_interno("admin"))],
)
async def cancelar(
    assinatura_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = AssinaturaRepository(db)
    a = await repo.get(assinatura_id)
    if a is None or a.conta_id != conta.id:
        raise NotFoundError("Assinatura não encontrada")
    svc = AssinaturaService(db)
    a = await svc.cancelar(a)
    await db.commit()
    return a


# === Faturas ===

@router.get("/faturas/", response_model=list[FaturaRead])
async def listar_faturas(
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    out: list = []
    repo_ass = AssinaturaRepository(db)
    repo_fat = FaturaRepository(db)
    for a in await repo_ass.listar_da_conta(conta.id):
        out.extend(await repo_fat.listar_da_assinatura(a.id))
    out.sort(key=lambda f: f.ciclo_inicio, reverse=True)
    return out


@router.post(
    "/faturas/{fatura_id}/pagar",
    response_model=OkResponse,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def pagar_fatura(
    fatura_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
    metodo: PagamentoMetodo = PagamentoMetodo.CARTAO,
):
    repo_fat = FaturaRepository(db)
    fatura = await repo_fat.get(fatura_id)
    if fatura is None:
        raise NotFoundError("Fatura não encontrada")
    repo_ass = AssinaturaRepository(db)
    ass = await repo_ass.get(fatura.assinatura_id)
    if ass is None or ass.conta_id != conta.id:
        raise ForbiddenError("Fatura não pertence à Conta ativa")

    svc = AssinaturaService(db)
    # MVP: marca como aprovado (integração com gateway plugável aqui)
    await svc.registrar_pagamento(
        fatura=fatura,
        valor_centavos=fatura.valor_centavos,
        metodo=metodo,
        status=PagamentoStatus.APROVADO,
        mensagem="Pagamento manual via API",
    )
    await db.commit()
    return OkResponse(ok=True)
