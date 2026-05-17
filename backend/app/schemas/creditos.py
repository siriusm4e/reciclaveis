"""Schemas — TransacaoCredito, PacoteCredito, Plano, Assinatura, Fatura, Pagamento."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

from app.models.enums import (
    AssinaturaStatus,
    FaturaStatus,
    PagamentoMetodo,
    PagamentoStatus,
    PapelTipo,
    TransacaoTipo,
)
from app.schemas.common import ORMModel, TimestampedORM


# === Créditos ===

class SaldoCreditos(ORMModel):
    conta_id: UUID
    saldo: int


class TransacaoCreditoRead(TimestampedORM):
    conta_id: UUID
    tipo: TransacaoTipo
    valor: int
    descricao: str
    referencia_tipo: str | None
    referencia_id: UUID | None
    admin_id: UUID | None


class CompraPacoteRequest(BaseModel):
    pacote_id: UUID
    metodo: PagamentoMetodo


# === PacoteCredito ===

class PacoteCreditoBase(BaseModel):
    nome: Annotated[str, StringConstraints(max_length=80)]
    descricao: str | None = None
    creditos: int = Field(gt=0)
    bonus: int = Field(ge=0, default=0)
    preco_centavos: int = Field(gt=0)
    ordem: int = 100
    ativo: bool = True


class PacoteCreditoCreate(PacoteCreditoBase): ...


class PacoteCreditoRead(PacoteCreditoBase, TimestampedORM): ...


# === Plano ===

class PlanoBase(BaseModel):
    papel: PapelTipo
    nome: Annotated[str, StringConstraints(max_length=80)]
    descricao: str | None = None
    limite_publicacoes_ativas: int = Field(ge=0)
    permite_alerta_pago: bool = False
    preco_mensal_centavos: int = Field(ge=0)
    gratuito: bool = False
    ativo: bool = True


class PlanoCreate(PlanoBase): ...


class PlanoRead(PlanoBase, TimestampedORM): ...


# === Assinatura ===

class AssinaturaCreate(BaseModel):
    papel_id: UUID
    plano_id: UUID


class AssinaturaRead(TimestampedORM):
    conta_id: UUID
    papel_id: UUID
    plano_id: UUID
    status: AssinaturaStatus
    data_inicio: datetime
    data_renovacao: datetime
    em_graca_desde: datetime | None
    pausada_desde: datetime | None
    cancelada_em: datetime | None
    ciclo_cortesia: bool


# === Fatura ===

class FaturaRead(TimestampedORM):
    assinatura_id: UUID
    ciclo_inicio: datetime
    ciclo_fim: datetime
    valor_centavos: int
    status: FaturaStatus
    vencimento: datetime


# === Pagamento ===

class PagamentoRead(TimestampedORM):
    fatura_id: UUID
    valor_centavos: int
    metodo: PagamentoMetodo
    status: PagamentoStatus
    tentativa: int
    gateway_id: str | None
    mensagem_gateway: str | None
