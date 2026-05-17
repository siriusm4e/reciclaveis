"""Rotas — Denúncias (abertura por usuário; resolução em api/admin)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa
from app.db.session import get_db
from app.models.conta import Conta
from app.models.denuncia import Denuncia
from app.repositories.moderacao import DenunciaRepository
from app.schemas.moderacao import DenunciaCreate, DenunciaRead

router = APIRouter(prefix="/api/denuncias", tags=["denuncias"])


@router.post(
    "/", response_model=DenunciaRead, status_code=status.HTTP_201_CREATED
)
async def abrir(
    payload: DenunciaCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    d = Denuncia(
        denunciante_conta_id=conta.id,
        alvo_tipo=payload.alvo_tipo,
        alvo_id=payload.alvo_id,
        tipo_fechado=payload.tipo_fechado,
        descricao=payload.descricao,
    )
    db.add(d)
    await db.commit()
    await db.refresh(d)
    return d


@router.get("/", response_model=list[DenunciaRead])
async def listar_minhas(
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await DenunciaRepository(db).listar_do_denunciante(conta.id)
