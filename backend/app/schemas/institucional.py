"""Schemas — PedidoColetaPublica, CampanhaPublica."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

from app.models.enums import CampanhaStatus, PedidoColetaStatus
from app.schemas.common import GeoPoint, ORMModel, TimestampedORM


# === PedidoColetaPublica ===

class PedidoColetaCreate(BaseModel):
    bairro: Annotated[str, StringConstraints(max_length=120)]
    cidade: Annotated[str, StringConstraints(max_length=100)]
    uf: Annotated[str, StringConstraints(pattern=r"^[A-Z]{2}$")]
    ibge_municipio: Annotated[str, StringConstraints(pattern=r"^\d{7}$")] | None = None
    tipo_residuo: Annotated[str, StringConstraints(max_length=120)]
    foto_path: str | None = None
    quantidade_estimada: Decimal | None = None
    descricao: str | None = None
    localizacao: GeoPoint


class PedidoColetaRead(TimestampedORM):
    conta_solicitante_id: UUID
    prefeitura_conta_id: UUID | None
    bairro: str
    cidade: str
    uf: str
    ibge_municipio: str | None
    tipo_residuo: str
    foto_path: str | None
    quantidade_estimada: Decimal | None
    descricao: str | None
    lat: float
    lng: float
    status: PedidoColetaStatus


class PedidoColetaStatusUpdate(BaseModel):
    status: PedidoColetaStatus
    nota: str | None = None


# === CampanhaPublica ===

class CampanhaCreate(BaseModel):
    titulo: Annotated[str, StringConstraints(min_length=3, max_length=200)]
    descricao: Annotated[str, StringConstraints(min_length=10)]
    data_evento: datetime | None = None
    tipo_residuo: str | None = None
    beneficio: str | None = None
    cidade: str | None = None
    uf: str | None = None
    ibge_municipio: str | None = None


class CampanhaUpdate(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    data_evento: datetime | None = None
    tipo_residuo: str | None = None
    beneficio: str | None = None
    status: CampanhaStatus | None = None


class CampanhaRead(TimestampedORM):
    conta_organizadora_id: UUID
    titulo: str
    descricao: str
    data_evento: datetime | None
    tipo_residuo: str | None
    beneficio: str | None
    cidade: str | None
    uf: str | None
    ibge_municipio: str | None
    status: CampanhaStatus


# === MapaInstitucional ===

class MapaInstitucionalCelula(ORMModel):
    bairro: str
    cidade: str
    uf: str
    ibge_municipio: str | None
    anuncios_ativos: int = Field(ge=0)
    pedidos_abertos: int = Field(ge=0)
    campanhas_ativas: int = Field(ge=0)


class MapaInstitucionalResposta(ORMModel):
    territorio: str  # "municipio:3550308" | "estado:SP"
    celulas: list[MapaInstitucionalCelula]
