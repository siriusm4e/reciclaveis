"""Rotas — Negociacao + ações (sinalizar/confirmar combinado, concluir, cancelar, disputar)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, get_current_user
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.conta import Conta
from app.models.negociacao import Negociacao
from app.models.usuario import Usuario
from app.repositories.negociacao import NegociacaoRepository
from app.schemas.common import OkResponse
from app.schemas.negociacao import (
    NegociacaoCancel,
    NegociacaoCreate,
    NegociacaoLocalizacaoExata,
    NegociacaoRead,
)
from app.services.negociacao_service import NegociacaoService

router = APIRouter(prefix="/api/negociacoes", tags=["negociacao"])


@router.post(
    "/", response_model=NegociacaoRead, status_code=status.HTTP_201_CREATED
)
async def abrir(
    payload: NegociacaoCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = NegociacaoService(db)
    neg = await svc.abrir(
        publicacao_id=payload.publicacao_id,
        publicacao_tipo=payload.publicacao_tipo,
        conta_iniciadora_id=conta.id,
    )
    await db.commit()
    await db.refresh(neg)
    return neg


@router.get("/", response_model=list[NegociacaoRead])
async def listar(
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await NegociacaoRepository(db).listar_da_conta(conta.id)


@router.get("/{negociacao_id}", response_model=NegociacaoRead)
async def detalhe(
    negociacao_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    neg = await _neg_da_conta(db, negociacao_id, conta)
    return neg


# === Ações ===

@router.post("/{negociacao_id}/sinalizar-combinado", response_model=NegociacaoRead)
async def sinalizar_combinado(
    negociacao_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    neg = await _neg_da_conta(db, negociacao_id, conta)
    svc = NegociacaoService(db)
    neg = await svc.sinalizar_combinado(negociacao=neg, conta_id=conta.id)
    await db.commit()
    await db.refresh(neg)
    return neg


@router.post("/{negociacao_id}/confirmar-combinado", response_model=NegociacaoRead)
async def confirmar_combinado(
    negociacao_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    neg = await _neg_da_conta(db, negociacao_id, conta)
    svc = NegociacaoService(db)
    neg = await svc.confirmar_combinado(negociacao=neg, conta_id=conta.id)
    await db.commit()
    await db.refresh(neg)
    return neg


@router.post("/{negociacao_id}/aceitar-localizacao", response_model=NegociacaoRead)
async def aceitar_localizacao(
    negociacao_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    neg = await _neg_da_conta(db, negociacao_id, conta)
    svc = NegociacaoService(db)
    neg = await svc.aceitar_localizacao_exata(negociacao=neg, conta_id=conta.id)
    await db.commit()
    await db.refresh(neg)
    return neg


@router.get(
    "/{negociacao_id}/localizacao-exata",
    response_model=NegociacaoLocalizacaoExata,
)
async def get_localizacao_exata(
    negociacao_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    neg = await _neg_da_conta(db, negociacao_id, conta)
    svc = NegociacaoService(db)
    lat, lng = await svc.revelar_localizacao_exata(neg)
    return NegociacaoLocalizacaoExata(lat=lat, lng=lng)


@router.post("/{negociacao_id}/concluir", response_model=NegociacaoRead)
async def concluir(
    negociacao_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    neg = await _neg_da_conta(db, negociacao_id, conta)
    svc = NegociacaoService(db)
    neg = await svc.concluir(negociacao=neg, conta_id=conta.id)
    await db.commit()
    await db.refresh(neg)
    return neg


@router.post("/{negociacao_id}/cancelar", response_model=NegociacaoRead)
async def cancelar(
    negociacao_id: UUID,
    payload: NegociacaoCancel,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    neg = await _neg_da_conta(db, negociacao_id, conta)
    svc = NegociacaoService(db)
    neg = await svc.cancelar(
        negociacao=neg, conta_id=conta.id, motivo=payload.motivo, texto=payload.texto
    )
    await db.commit()
    await db.refresh(neg)
    return neg


@router.post("/{negociacao_id}/disputar", response_model=NegociacaoRead)
async def disputar(
    negociacao_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    neg = await _neg_da_conta(db, negociacao_id, conta)
    svc = NegociacaoService(db)
    neg = await svc.disputar(negociacao=neg, conta_id=conta.id)
    await db.commit()
    await db.refresh(neg)
    return neg


# === Helper ===

async def _neg_da_conta(
    db: AsyncSession, negociacao_id: UUID, conta: Conta
) -> Negociacao:
    neg = await NegociacaoRepository(db).get(negociacao_id)
    if neg is None:
        raise NotFoundError("Negociação não encontrada")
    if conta.id not in (neg.conta_vendedora_id, neg.conta_compradora_id):
        raise ForbiddenError("Conta não participa desta Negociação")
    return neg


_ = get_current_user
_ = OkResponse
