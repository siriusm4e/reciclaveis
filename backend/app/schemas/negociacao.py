"""Schemas — Negociacao, Mensagem, Avaliacao, Oportunidade, Proposta."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

from app.models.enums import (
    MensagemTipo,
    MotivoCancelamento,
    NegociacaoStatus,
    OportunidadeStatus,
    OportunidadeTipo,
    PapelTipo,
    PropostaStatus,
    PublicacaoTipo,
)
from app.schemas.common import ORMModel, TimestampedORM


# === Negociacao ===

class NegociacaoCreate(BaseModel):
    publicacao_id: UUID
    publicacao_tipo: PublicacaoTipo


class NegociacaoRead(TimestampedORM):
    publicacao_id: UUID
    publicacao_tipo: PublicacaoTipo
    conta_vendedora_id: UUID
    conta_compradora_id: UUID
    status: NegociacaoStatus
    aceite_localizacao_exata_vendedor: bool
    aceite_localizacao_exata_comprador: bool
    combinada_em: datetime | None
    motivo_cancelamento: MotivoCancelamento | None
    motivo_cancelamento_texto: str | None
    ultima_mensagem_em: datetime | None
    ultima_mensagem_preview: str | None


class NegociacaoCancel(BaseModel):
    motivo: MotivoCancelamento
    texto: Annotated[str, StringConstraints(min_length=3, max_length=500)]


class NegociacaoLocalizacaoExata(ORMModel):
    lat: float
    lng: float


# === Mensagem ===

class MensagemCreate(BaseModel):
    conteudo: Annotated[str, StringConstraints(min_length=1, max_length=4000)]


class MensagemRead(TimestampedORM):
    negociacao_id: UUID
    conta_remetente_id: UUID
    usuario_remetente_id: UUID | None
    conteudo: str
    tipo: MensagemTipo


# === Avaliação ===

class AvaliacaoCreate(BaseModel):
    nota: int = Field(ge=1, le=5)
    papel_avaliado: PapelTipo
    subnotas: dict = Field(default_factory=dict)
    comentario: str | None = Field(default=None, max_length=2000)


class AvaliacaoRead(TimestampedORM):
    negociacao_id: UUID
    avaliador_conta_id: UUID
    avaliado_conta_id: UUID
    papel_avaliado: PapelTipo
    nota: int
    subnotas: dict
    comentario: str | None
    visivel: bool
    removida: bool


# === Oportunidade ===

class OportunidadeCreate(BaseModel):
    titulo: Annotated[str, StringConstraints(min_length=5, max_length=200)]
    descricao: Annotated[str, StringConstraints(min_length=10)]
    subcategoria_id: UUID
    tipo: OportunidadeTipo
    documentos_exigidos: list[str] = Field(default_factory=list)
    prazo_submissao: datetime
    valor_estimado: Decimal | None = None


class OportunidadeRead(TimestampedORM):
    conta_id: UUID
    titulo: str
    descricao: str
    subcategoria_id: UUID
    tipo: OportunidadeTipo
    documentos_exigidos: list[str]
    prazo_submissao: datetime
    valor_estimado: Decimal | None
    status: OportunidadeStatus
    proposta_vencedora_id: UUID | None


# === Proposta ===

class PropostaCreate(BaseModel):
    valor: Decimal = Field(gt=0)
    condicoes: str | None = None
    documentos_anexos: list[str] = Field(default_factory=list)


class PropostaRead(TimestampedORM):
    oportunidade_id: UUID
    conta_proponente_id: UUID
    valor: Decimal
    condicoes: str | None
    documentos_anexos: list[str]
    status: PropostaStatus
