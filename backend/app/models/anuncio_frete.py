"""AnuncioFrete — capacidade de frete de Conta com Papel=Freteiro.

`categorias_residuo_aceitas` filtra a aparição em buscas. Freteiro que não
aceita 'hospitalar' não aparece em buscas de frete hospitalar.
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
from app.models.enums import AnuncioStatus

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.papel import PapelAtivado


class AnuncioFrete(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "anuncio_frete"
    __table_args__ = (
        Index("ix_anuncio_frete_geom_gist", "geom", postgresql_using="gist"),
    )

    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    papel_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("papel_ativado.id", ondelete="RESTRICT"), nullable=False
    )

    tipo_veiculo: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    capacidade_t: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    capacidade_m3: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    tara: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)

    raio_operacional_km: Mapped[int] = mapped_column(Integer, nullable=False)
    # Categorias (slugs) que o frete aceita transportar.
    categorias_residuo_aceitas: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    licencas: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    emite_nf: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    geom: Mapped[object] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )

    prazo_validade: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[AnuncioStatus] = mapped_column(
        SAEnum(AnuncioStatus, name="anuncio_status", create_type=False),
        default=AnuncioStatus.RASCUNHO,
        nullable=False,
        index=True,
    )

    conta: Mapped["Conta"] = relationship("Conta")
    papel: Mapped["PapelAtivado"] = relationship("PapelAtivado")
