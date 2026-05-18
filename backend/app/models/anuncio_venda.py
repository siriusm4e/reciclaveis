"""AnuncioVenda — oferta de material à venda por uma Conta vendedora.

Privacidade de localização:
- lat_real/lng_real: NUNCA expostos em endpoint público.
- lat_pub/lng_pub: calculados UMA VEZ com offset (urbano ≥ 200m, rural ≥ 1km),
  persistidos e usados em buscas (`geom_pub` indexado por GIST).
- lat_real só é liberado em endpoint de Negociação aceita (status≥combinada
  e aceite_localizacao_exata=true).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import (
    AnuncioVendaStatus,
    CondicaoForma,
    CondicaoLimpeza,
    CondicaoUmidade,
    FrequenciaAnuncio,
)

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.papel import PapelAtivado
    from app.models.tipo_material import TipoMaterial


class AnuncioVenda(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "anuncio_venda"
    __table_args__ = (
        # geom_pub é o que entra em buscas públicas — GIST obrigatório.
        Index("ix_anuncio_venda_geom_pub_gist", "geom_pub", postgresql_using="gist"),
        Index("ix_anuncio_venda_status_validade", "status", "prazo_validade"),
    )

    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    papel_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("papel_ativado.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    tipo_material_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tipo_material.id"), nullable=False, index=True
    )

    # Identificação do anúncio = Categoria + Subcategoria + Tipo + Condição.
    # Sem campos de título/descrição livre (decisão de produto pós-homologação).

    # Atributos comuns + específicos do TipoMaterial validados no service
    atributos: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # === Condição (grupos exclusivos no formulário) ===
    # values_callable força SQLAlchemy a usar o .value (lowercase) ao serializar
    # — o tipo Postgres foi criado com labels lowercase em 0003. Sem isso, o
    # default seria .name (uppercase) e qualquer INSERT falharia com
    # `invalid input value for enum`.
    condicao_limpeza: Mapped[CondicaoLimpeza | None] = mapped_column(
        SAEnum(
            CondicaoLimpeza,
            name="condicao_limpeza",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=True,
    )
    condicao_umidade: Mapped[CondicaoUmidade | None] = mapped_column(
        SAEnum(
            CondicaoUmidade,
            name="condicao_umidade",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=True,
    )
    condicao_forma: Mapped[CondicaoForma | None] = mapped_column(
        SAEnum(
            CondicaoForma,
            name="condicao_forma",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=True,
    )

    # === Privacidade de localização ===
    # Localização REAL — nunca exposta publicamente
    lat_real: Mapped[float] = mapped_column(Float, nullable=False)
    lng_real: Mapped[float] = mapped_column(Float, nullable=False)
    # Localização PÚBLICA com offset aplicado uma vez
    lat_pub: Mapped[float] = mapped_column(Float, nullable=False)
    lng_pub: Mapped[float] = mapped_column(Float, nullable=False)
    offset_m: Mapped[float] = mapped_column(Float, nullable=False)
    geom_pub: Mapped[object] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )
    # Classificação urbano/rural decide offset mínimo
    territorio: Mapped[str] = mapped_column(String(10), nullable=False)  # urbano | rural

    # === Preço / unidade / volume ===
    preco_pretendido: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unidade: Mapped[str] = mapped_column(String(20), nullable=False)  # herdada da Subcategoria
    volume_estimado: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    # === Frequência ===
    frequencia: Mapped[FrequenciaAnuncio] = mapped_column(
        SAEnum(FrequenciaAnuncio, name="frequencia_anuncio"),
        default=FrequenciaAnuncio.LOTE_UNICO,
        nullable=False,
    )
    intervalo_geracao: Mapped[str | None] = mapped_column(String(60), nullable=True)  # ex.: "semanal", "mensal"

    # === Ciclo de vida ===
    prazo_validade: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[AnuncioVendaStatus] = mapped_column(
        SAEnum(AnuncioVendaStatus, name="anuncio_venda_status"),
        default=AnuncioVendaStatus.RASCUNHO,
        nullable=False,
        index=True,
    )

    # === Mídia ===
    fotos: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    # === Privacidade de Negociação ===
    aceita_alerta_pago_de_terceiros: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Contadores leves
    visualizacoes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    conta: Mapped["Conta"] = relationship("Conta")
    papel: Mapped["PapelAtivado"] = relationship("PapelAtivado")
    tipo_material: Mapped["TipoMaterial"] = relationship("TipoMaterial")
