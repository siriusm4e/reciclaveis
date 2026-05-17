"""Rotas — Campanhas Públicas."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, require_papel_interno
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.campanha_publica import CampanhaPublica
from app.models.conta import Conta, ContaTipo
from app.models.enums import CampanhaStatus
from app.models.preferencia_comunicacao import PreferenciaComunicacao
from app.repositories.institucional import CampanhaRepository
from app.schemas.institucional import CampanhaCreate, CampanhaRead, CampanhaUpdate
from app.services.institucional_service import InstitucionalService

router = APIRouter(prefix="/api/campanhas", tags=["institucional"])


@router.post(
    "/",
    response_model=CampanhaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin"))],
)
async def criar(
    payload: CampanhaCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if conta.tipo != ContaTipo.ORGAO_PUBLICO:
        raise ForbiddenError("Campanhas só por Conta Órgão Público")
    svc = InstitucionalService(db)
    c = await svc.criar_campanha(
        conta_organizadora_id=conta.id,
        **payload.model_dump(),
    )
    await db.commit()
    await db.refresh(c)
    return c


@router.get("/", response_model=list[CampanhaRead])
async def listar(
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
    ibge: str | None = Query(default=None),
):
    # Só exibir para Contas com aceita_comunicacao_prefeitura_municipio = true
    pref = await db.scalar(
        select(PreferenciaComunicacao).where(PreferenciaComunicacao.conta_id == conta.id)
    )
    if pref and not pref.aceita_comunicacao_prefeitura_municipio:
        return []
    if not ibge:
        return []
    return await CampanhaRepository(db).listar_publicadas_para_municipio(ibge)


@router.patch("/{campanha_id}", response_model=CampanhaRead)
async def atualizar(
    campanha_id: UUID,
    payload: CampanhaUpdate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = CampanhaRepository(db)
    c = await repo.get(campanha_id)
    if c is None or c.conta_organizadora_id != conta.id:
        raise NotFoundError("Campanha não encontrada")
    svc = InstitucionalService(db)
    c = await svc.atualizar_campanha(c, **payload.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(c)
    return c


_ = CampanhaPublica
_ = CampanhaStatus
