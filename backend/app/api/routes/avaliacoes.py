"""Rotas — Avaliações da Negociação concluída + reputação por Conta."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa
from app.db.session import get_db
from app.models.conta import Conta
from app.repositories.negociacao import AvaliacaoRepository
from app.schemas.identidade import ReputacaoConta, ReputacaoPorPapel
from app.schemas.negociacao import AvaliacaoCreate, AvaliacaoRead
from app.services.reputacao_service import ReputacaoService

router = APIRouter(prefix="/api", tags=["reputacao"])


@router.post(
    "/negociacoes/{negociacao_id}/avaliacoes",
    response_model=AvaliacaoRead,
    status_code=status.HTTP_201_CREATED,
)
async def avaliar(
    negociacao_id: UUID,
    payload: AvaliacaoCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = ReputacaoService(db)
    av = await svc.avaliar(
        negociacao_id=negociacao_id,
        avaliador_conta_id=conta.id,
        nota=payload.nota,
        papel_avaliado=payload.papel_avaliado,
        subnotas=payload.subnotas,
        comentario=payload.comentario,
    )
    await db.commit()
    await db.refresh(av)
    return av


@router.get("/contas/{conta_id}/reputacao", response_model=ReputacaoConta)
async def reputacao_conta(
    conta_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = ReputacaoService(db)
    por_papel = await svc.reputacao_por_papel(conta_id)
    return ReputacaoConta(
        conta_id=conta_id,
        por_papel=[ReputacaoPorPapel(**p) for p in por_papel],
    )


_ = AvaliacaoRepository  # keep import alive
