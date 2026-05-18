"""Rotas — Analytics públicas (preço de referência ao próprio vendedor)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.core.deps import get_conta_ativa
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.conta import Conta
from app.models.tipo_material import TipoMaterial
from app.repositories.marketplace import AnuncioVendaRepository
from app.schemas.analytics import PrecoReferenciaResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/anuncios-venda", tags=["analytics"])


@router.get(
    "/{anuncio_id}/preco-referencia",
    response_model=PrecoReferenciaResponse,
)
async def preco_referencia(
    anuncio_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
    cidade: str | None = Query(default=None),
):
    """Exibido SOMENTE ao próprio vendedor e com amostra ≥ 5."""
    repo = AnuncioVendaRepository(db)
    anuncio = await repo.get(anuncio_id)
    if anuncio is None:
        raise NotFoundError("Anúncio não encontrado")
    if anuncio.conta_id != conta.id:
        raise ForbiddenError("Preço de referência só visível ao próprio vendedor")
    # Preço de referência é agregado ao nível Subcategoria (intermediária).
    # Resolve a subcategoria a partir do tipo_material do anúncio.
    tipo = await db.scalar(
        select(TipoMaterial).where(TipoMaterial.id == anuncio.tipo_material_id)
    )
    if tipo is None:
        raise NotFoundError("Tipo de material do anúncio não encontrado")
    svc = AnalyticsService(db)
    return PrecoReferenciaResponse(**await svc.preco_referencia(
        subcategoria_id=tipo.subcategoria_id, cidade=cidade
    ))
