"""Schemas — Conta, Membro, Papel, Estabelecimento, Convite."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, StringConstraints

from app.models.enums import (
    ContaStatus,
    ContaTipo,
    ConviteStatus,
    PapelInternoMembro,
    PapelStatus,
    PapelTipo,
)
from app.schemas.common import GeoPoint, ORMModel, TimestampedORM


# === Conta ===

class ContaCreate(BaseModel):
    tipo: ContaTipo
    nome_publico: Annotated[str, StringConstraints(min_length=2, max_length=255)]
    cnpj: Annotated[str, StringConstraints(pattern=r"^\d{14}$")] | None = None
    escopo_territorial: dict | None = None


class ContaUpdate(BaseModel):
    nome_publico: str | None = None
    foto_perfil_path: str | None = None
    escopo_territorial: dict | None = None


class ContaRead(TimestampedORM):
    tipo: ContaTipo
    status: ContaStatus
    nome_publico: str
    cnpj: str | None
    foto_perfil_path: str | None
    escopo_territorial: dict | None
    cortesia_ativa: bool


class ContaStatusUpdate(BaseModel):
    """Backoffice — aprova, suspende, anonimiza."""

    status: ContaStatus
    motivo: Annotated[str, StringConstraints(min_length=3, max_length=500)]


# === Membro / Convite ===

class MembroRead(TimestampedORM):
    usuario_id: UUID
    conta_id: UUID
    papel_interno: PapelInternoMembro


class ConviteCreate(BaseModel):
    email: EmailStr
    papel_interno: PapelInternoMembro = PapelInternoMembro.OPERADOR


class ConviteRead(TimestampedORM):
    conta_id: UUID
    email: EmailStr
    papel_interno: PapelInternoMembro
    expira_em: datetime
    status: ConviteStatus


class ConviteAceitar(BaseModel):
    token: Annotated[str, StringConstraints(min_length=20, max_length=128)]


# === Papel Ativado ===

class PapelCreate(BaseModel):
    papel: PapelTipo
    dados_complementares: dict = Field(default_factory=dict)


class PapelUpdate(BaseModel):
    dados_complementares: dict | None = None
    status: PapelStatus | None = None


class PapelRead(TimestampedORM):
    conta_id: UUID
    papel: PapelTipo
    status: PapelStatus
    dados_complementares: dict


# === Estabelecimento ===

class EstabelecimentoCreate(BaseModel):
    nome: Annotated[str, StringConstraints(min_length=2, max_length=255)]
    cep: Annotated[str, StringConstraints(pattern=r"^\d{8}$")]
    logradouro: Annotated[str, StringConstraints(min_length=2, max_length=255)]
    numero: Annotated[str, StringConstraints(max_length=20)]
    complemento: str | None = None
    bairro: Annotated[str, StringConstraints(max_length=100)]
    cidade: Annotated[str, StringConstraints(max_length=100)]
    uf: Annotated[str, StringConstraints(pattern=r"^[A-Z]{2}$")]
    ibge_municipio: Annotated[str, StringConstraints(pattern=r"^\d{7}$")] | None = None
    localizacao: GeoPoint


class EstabelecimentoRead(TimestampedORM):
    conta_id: UUID
    nome: str
    cep: str
    logradouro: str
    numero: str
    complemento: str | None
    bairro: str
    cidade: str
    uf: str
    ibge_municipio: str | None
    lat: float
    lng: float


# === Reputação ===

class ReputacaoPorPapel(ORMModel):
    papel: PapelTipo
    media: float = Field(ge=0, le=5)
    total_avaliacoes: int = Field(ge=0)


class ReputacaoConta(ORMModel):
    conta_id: UUID
    por_papel: list[ReputacaoPorPapel]
