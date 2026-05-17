"""OfertaCompra — demanda de compra publicada por Conta compradora.

Alerta Pago é boost EMBUTIDO na OfertaCompra (não entidade autônoma):
- boost_ativo / boost_raio_km / boost_duracao_horas / boost_segmentacao.
- Disparo do boost calcula Cobertura (Contas vendedoras elegíveis no raio).
- Cobertura < limiar configurável → Créditos devolvidos, nenhum push enviado.
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
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import OfertaCompraStatus

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.papel import PapelAtivado
    from app.models.subcategoria import Subcategoria


class OfertaCompra(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "oferta_compra"
    __table_args__ = (
        Index("ix_oferta_compra_geom_gist", "geom", postgresql_using="gist"),
    )

    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    papel_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("papel_ativado.id", ondelete="RESTRICT"), nullable=False
    )
    subcategoria_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("subcategoria.id"), nullable=False, index=True
    )

    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    especificacao: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    preco_paga: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unidade: Mapped[str] = mapped_column(String(20), nullable=False)
    volume_min: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    volume_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    # Localização do comprador (Estabelecimento principal — não tem privacidade
    # ofuscada, é endereço comercial de quem compra).
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    raio_km: Mapped[int] = mapped_column(Integer, nullable=False)
    geom: Mapped[object] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )

    retira: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    prazo_validade: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[OfertaCompraStatus] = mapped_column(
        SAEnum(OfertaCompraStatus, name="oferta_compra_status"),
        default=OfertaCompraStatus.RASCUNHO,
        nullable=False,
        index=True,
    )

    # === Boost / Alerta Pago ===
    boost_ativo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    boost_raio_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    boost_duracao_horas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    boost_inicio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    boost_fim: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Segmentação adicional (papéis, urbano/rural, frequência, etc.)
    boost_segmentacao: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    # Auditoria do disparo: cobertura calculada, push enviado, reembolso aplicado
    boost_auditoria: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    conta: Mapped["Conta"] = relationship("Conta")
    papel: Mapped["PapelAtivado"] = relationship("PapelAtivado")
    subcategoria: Mapped["Subcategoria"] = relationship("Subcategoria")
