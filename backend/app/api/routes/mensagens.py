"""Rotas — Mensagens dentro de uma Negociação."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, get_current_user
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.conta import Conta
from app.models.usuario import Usuario
from app.repositories.negociacao import MensagemRepository, NegociacaoRepository
from app.schemas.negociacao import MensagemCreate, MensagemRead
from app.services.negociacao_service import NegociacaoService

router = APIRouter(prefix="/api/negociacoes/{negociacao_id}/mensagens", tags=["negociacao"])


@router.get("/", response_model=list[MensagemRead])
async def listar(
    negociacao_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    neg = await NegociacaoRepository(db).get(negociacao_id)
    if neg is None:
        raise NotFoundError("Negociação não encontrada")
    if conta.id not in (neg.conta_vendedora_id, neg.conta_compradora_id):
        raise ForbiddenError("Conta não participa")
    return await MensagemRepository(db).listar_da_negociacao(negociacao_id)


@router.post(
    "/", response_model=MensagemRead, status_code=status.HTTP_201_CREATED
)
async def enviar(
    negociacao_id: UUID,
    payload: MensagemCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    neg = await NegociacaoRepository(db).get(negociacao_id)
    if neg is None:
        raise NotFoundError("Negociação não encontrada")
    svc = NegociacaoService(db)
    msg = await svc.enviar_mensagem(
        negociacao=neg,
        conta_remetente_id=conta.id,
        usuario_remetente_id=current_user.id,
        conteudo=payload.conteudo,
    )
    await db.commit()
    await db.refresh(msg)
    return msg
