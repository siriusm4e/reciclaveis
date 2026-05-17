"""Schemas — Analytics (M14)."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.schemas.common import ORMModel


class PrecoMedioPorTerritorio(ORMModel):
    subcategoria_id: UUID
    uf: str | None
    cidade: str | None
    amostra: int = Field(ge=0)
    preco_medio: Decimal | None = None


class PrecoReferenciaResponse(ORMModel):
    """Exibido ao vendedor SOMENTE quando amostra >= 5."""

    subcategoria_id: UUID
    cidade: str | None
    amostra: int
    preco_medio: Decimal | None


class MapaCalorCelula(ORMModel):
    uf: str | None
    cidade: str | None
    densidade_oferta: int
    densidade_demanda: int


class PublicacoesAtivasPorSubcategoria(ORMModel):
    subcategoria_id: UUID
    nome: str
    total: int


class LiquidezPorSubcategoria(ORMModel):
    subcategoria_id: UUID
    nome: str
    ofertas: int
    demandas: int
    razao: float | None
