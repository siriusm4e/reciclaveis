"""Schemas — AnuncioVenda, OfertaCompra, AnuncioMaquina, AnuncioServico, AnuncioFrete, AssinaturaAlerta."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints, field_validator

from app.models.enums import (
    AnuncioStatus,
    AnuncioVendaStatus,
    CondicaoEquipamento,
    CondicaoForma,
    CondicaoLimpeza,
    CondicaoUmidade,
    FrequenciaAnuncio,
    ModalidadeMaquina,
    OfertaCompraStatus,
    UnidadeCobrancaServico,
)
from app.schemas.common import GeoPoint, ORMModel, TimestampedORM


def _validar_raio_km(v: int | None) -> int | None:
    """Validador compartilhado: raio entre 1 e 500 km (mensagem PT-BR)."""
    if v is None:
        return v
    if v < 1 or v > 500:
        raise ValueError("Raio deve estar entre 1 e 500 km")
    return v


# === AnuncioVenda ===

class AnuncioVendaCreate(BaseModel):
    """Anúncio identificado por Categoria + Subcategoria + Tipo + Condição.

    Não há título nem descrição livre — decisão de produto pós-homologação.
    """

    papel_id: UUID
    tipo_material_id: UUID
    atributos: dict = Field(default_factory=dict)
    # === Condição (grupos exclusivos no formulário) ===
    condicao_limpeza: CondicaoLimpeza | None = None
    condicao_umidade: CondicaoUmidade | None = None
    condicao_forma: CondicaoForma | None = None
    # Localização REAL — recebida do app, ofuscada no service antes de persistir
    localizacao_real: GeoPoint
    territorio: Annotated[str, StringConstraints(pattern=r"^(urbano|rural)$")]
    preco_pretendido: Decimal = Field(gt=0)
    unidade: Annotated[str, StringConstraints(max_length=20)]
    volume_estimado: Decimal | None = Field(default=None, gt=0)
    frequencia: FrequenciaAnuncio = FrequenciaAnuncio.LOTE_UNICO
    intervalo_geracao: str | None = None
    prazo_validade: datetime
    # Fotos: opcionais, máximo 3
    fotos: list[str] = Field(default_factory=list, max_length=3)
    aceita_alerta_pago_de_terceiros: bool = True


class AnuncioVendaUpdate(BaseModel):
    atributos: dict | None = None
    condicao_limpeza: CondicaoLimpeza | None = None
    condicao_umidade: CondicaoUmidade | None = None
    condicao_forma: CondicaoForma | None = None
    preco_pretendido: Decimal | None = None
    volume_estimado: Decimal | None = None
    prazo_validade: datetime | None = None
    status: AnuncioVendaStatus | None = None
    fotos: list[str] | None = Field(default=None, max_length=3)
    aceita_alerta_pago_de_terceiros: bool | None = None


class AnuncioVendaRead(TimestampedORM):
    """Versão pública — NUNCA expõe lat_real/lng_real."""

    conta_id: UUID
    papel_id: UUID
    tipo_material_id: UUID
    atributos: dict
    condicao_limpeza: CondicaoLimpeza | None
    condicao_umidade: CondicaoUmidade | None
    condicao_forma: CondicaoForma | None
    # Localização aproximada (oferta_m embutido na precisão)
    lat_pub: float
    lng_pub: float
    offset_m: float
    territorio: str
    preco_pretendido: Decimal
    unidade: str
    volume_estimado: Decimal | None
    frequencia: FrequenciaAnuncio
    intervalo_geracao: str | None
    prazo_validade: datetime
    status: AnuncioVendaStatus
    fotos: list[str]
    aceita_alerta_pago_de_terceiros: bool
    visualizacoes: int


class AnuncioVendaSearch(BaseModel):
    categoria_id: UUID | None = None
    subcategoria_id: UUID | None = None
    tipo_material_id: UUID | None = None
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    raio_km: int | None = None
    preco_min: Decimal | None = None
    preco_max: Decimal | None = None
    # Volume mínimo do anúncio em kg que o comprador exige (filtro mútuo)
    volume_minimo_kg: float | None = Field(default=None, ge=0)
    condicao_limpeza: CondicaoLimpeza | None = None
    condicao_umidade: CondicaoUmidade | None = None
    condicao_forma: CondicaoForma | None = None

    @field_validator("raio_km")
    @classmethod
    def _val_raio(cls, v: int | None) -> int | None:
        return _validar_raio_km(v)


# === OfertaCompra ===

class OfertaCompraCreate(BaseModel):
    papel_id: UUID
    tipo_material_id: UUID
    titulo: Annotated[str, StringConstraints(min_length=3, max_length=150)]
    descricao: str | None = None
    especificacao: dict = Field(default_factory=dict)
    preco_paga: Decimal = Field(gt=0)
    unidade: Annotated[str, StringConstraints(max_length=20)]
    volume_min: Decimal = Field(gt=0)
    volume_max: Decimal | None = Field(default=None, gt=0)
    # Volume mínimo (kg) que o vendedor precisa ter para ver esta oferta
    volume_minimo_kg: float | None = Field(default=None, ge=0)
    # Condição buscada (filtro)
    condicao_limpeza: CondicaoLimpeza | None = None
    condicao_umidade: CondicaoUmidade | None = None
    condicao_forma: CondicaoForma | None = None
    localizacao: GeoPoint
    raio_km: int
    retira: bool = False
    prazo_validade: datetime

    @field_validator("raio_km")
    @classmethod
    def _val_raio(cls, v: int) -> int:
        return _validar_raio_km(v)  # type: ignore[return-value]


class OfertaCompraUpdate(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    especificacao: dict | None = None
    preco_paga: Decimal | None = None
    volume_min: Decimal | None = None
    volume_max: Decimal | None = None
    volume_minimo_kg: float | None = Field(default=None, ge=0)
    condicao_limpeza: CondicaoLimpeza | None = None
    condicao_umidade: CondicaoUmidade | None = None
    condicao_forma: CondicaoForma | None = None
    raio_km: int | None = None
    prazo_validade: datetime | None = None
    status: OfertaCompraStatus | None = None

    @field_validator("raio_km")
    @classmethod
    def _val_raio(cls, v: int | None) -> int | None:
        return _validar_raio_km(v)


class OfertaCompraRead(TimestampedORM):
    conta_id: UUID
    papel_id: UUID
    tipo_material_id: UUID
    titulo: str
    descricao: str | None
    especificacao: dict
    preco_paga: Decimal
    unidade: str
    volume_min: Decimal
    volume_max: Decimal | None
    volume_minimo_kg: float | None
    condicao_limpeza: CondicaoLimpeza | None
    condicao_umidade: CondicaoUmidade | None
    condicao_forma: CondicaoForma | None
    lat: float
    lng: float
    raio_km: int
    retira: bool
    prazo_validade: datetime
    status: OfertaCompraStatus
    boost_ativo: bool
    boost_raio_km: int | None
    boost_duracao_horas: int | None
    boost_inicio: datetime | None
    boost_fim: datetime | None


class AlertaPagoConfig(BaseModel):
    raio_km: int
    duracao_horas: int = Field(ge=1, le=168)
    segmentacao: dict = Field(default_factory=dict)

    @field_validator("raio_km")
    @classmethod
    def _val_raio(cls, v: int) -> int:
        return _validar_raio_km(v)  # type: ignore[return-value]


class AlertaPagoResultado(ORMModel):
    cobertura: int
    cobertura_minima: int
    disparou: bool
    creditos_debitados: int
    creditos_reembolsados: int
    oferta_id: UUID


# === AnuncioMaquina ===

class AnuncioMaquinaCreate(BaseModel):
    papel_id: UUID | None = None
    categoria_equipamento: Annotated[str, StringConstraints(max_length=100)]
    marca: str | None = None
    modelo: str | None = None
    ano: int | None = Field(default=None, ge=1900, le=2100)
    capacidade: str | None = None
    tensao: str | None = None
    descricao: str | None = None
    condicao: CondicaoEquipamento
    modalidade: ModalidadeMaquina
    aceita_visita_tecnica: bool = False
    disponibilidade: dict | None = None
    preco: Decimal = Field(gt=0)
    documentacao_disponivel: bool = False
    fotos: list[str] = Field(default_factory=list)
    localizacao: GeoPoint
    prazo_validade: datetime


class AnuncioMaquinaRead(TimestampedORM):
    conta_id: UUID
    papel_id: UUID | None
    categoria_equipamento: str
    marca: str | None
    modelo: str | None
    ano: int | None
    capacidade: str | None
    tensao: str | None
    descricao: str | None
    condicao: CondicaoEquipamento
    modalidade: ModalidadeMaquina
    aceita_visita_tecnica: bool
    disponibilidade: dict | None
    preco: Decimal
    documentacao_disponivel: bool
    fotos: list[str]
    lat: float
    lng: float
    prazo_validade: datetime
    status: AnuncioStatus


# === AnuncioServico ===

class AnuncioServicoCreate(BaseModel):
    papel_id: UUID
    tipo_servico: Annotated[str, StringConstraints(max_length=120)]
    descricao: str | None = None
    raio_operacional_km: int
    unidade_cobranca: UnidadeCobrancaServico
    preco: Decimal | None = Field(default=None, ge=0)
    requer_visita_tecnica: bool = False
    disponibilidade: dict | None = None
    localizacao: GeoPoint
    prazo_validade: datetime

    @field_validator("raio_operacional_km")
    @classmethod
    def _val_raio(cls, v: int) -> int:
        return _validar_raio_km(v)  # type: ignore[return-value]


class AnuncioServicoRead(TimestampedORM):
    conta_id: UUID
    papel_id: UUID
    tipo_servico: str
    descricao: str | None
    raio_operacional_km: int
    unidade_cobranca: UnidadeCobrancaServico
    preco: Decimal | None
    requer_visita_tecnica: bool
    disponibilidade: dict | None
    lat: float
    lng: float
    prazo_validade: datetime
    status: AnuncioStatus


# === AnuncioFrete ===

class AnuncioFreteCreate(BaseModel):
    papel_id: UUID
    tipo_veiculo: Annotated[str, StringConstraints(max_length=80)]
    capacidade_t: Decimal | None = Field(default=None, ge=0)
    capacidade_m3: Decimal | None = Field(default=None, ge=0)
    tara: Decimal | None = Field(default=None, ge=0)
    # Frete pode operar interestadual — raio maior que a regra padrão de 500km
    raio_operacional_km: int = Field(ge=1, le=2000)
    categorias_residuo_aceitas: list[str] = Field(default_factory=list)
    licencas: list[str] = Field(default_factory=list)
    emite_nf: bool = False
    localizacao: GeoPoint
    prazo_validade: datetime


class AnuncioFreteRead(TimestampedORM):
    conta_id: UUID
    papel_id: UUID
    tipo_veiculo: str
    capacidade_t: Decimal | None
    capacidade_m3: Decimal | None
    tara: Decimal | None
    raio_operacional_km: int
    categorias_residuo_aceitas: list[str]
    licencas: list[str]
    emite_nf: bool
    lat: float
    lng: float
    prazo_validade: datetime
    status: AnuncioStatus


# === AssinaturaAlerta ===

class AssinaturaAlertaCreate(BaseModel):
    papel_id: UUID
    categoria_id: UUID
    subcategoria_ids: list[str] = Field(default_factory=list)
    raio_km: int
    preco_min: Decimal | None = None

    @field_validator("raio_km")
    @classmethod
    def _val_raio(cls, v: int) -> int:
        return _validar_raio_km(v)  # type: ignore[return-value]


class AssinaturaAlertaUpdate(BaseModel):
    subcategoria_ids: list[str] | None = None
    raio_km: int | None = None
    preco_min: Decimal | None = None
    ativa: bool | None = None

    @field_validator("raio_km")
    @classmethod
    def _val_raio(cls, v: int | None) -> int | None:
        return _validar_raio_km(v)


class AssinaturaAlertaRead(TimestampedORM):
    conta_id: UUID
    papel_id: UUID
    categoria_id: UUID
    subcategoria_ids: list[str]
    raio_km: int
    preco_min: Decimal | None
    ativa: bool
