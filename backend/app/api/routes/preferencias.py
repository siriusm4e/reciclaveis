"""Rotas — PreferenciaComunicacao (opt-ins LGPD)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa
from app.db.session import get_db
from app.models.conta import Conta
from app.schemas.conteudo import (
    PreferenciaComunicacaoRead,
    PreferenciaComunicacaoUpdate,
)
from app.services.conteudo_service import ConteudoService

router = APIRouter(prefix="/api/preferencias-comunicacao", tags=["preferencias"])


@router.get("/", response_model=PreferenciaComunicacaoRead)
async def get_prefs(
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await ConteudoService(db).get_preferencias(conta.id)


@router.patch("/", response_model=PreferenciaComunicacaoRead)
async def update_prefs(
    payload: PreferenciaComunicacaoUpdate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = ConteudoService(db)
    p = await svc.atualizar_preferencias(conta.id, **payload.model_dump(exclude_unset=True))
    await db.commit()
    return p
