"""AnuncioServico — serviço oferecido por Prestador ou Gestor de Resíduos."""

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
from app.models.enums import AnuncioStatus, UnidadeCobrancaServico

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.papel import PapelAtivado


class AnuncioServico(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "anuncio_servico"
    __table_args__ = (
        Index("ix_anuncio_servico_geom_gist", "geom", postgresql_using="gist"),
    )

    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    papel_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("papel_ativado.id", ondelete="RESTRICT"), nullable=False
    )

    tipo_servico: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    raio_operacional_km: Mapped[int] = mapped_column(Integer, nullable=False)
    unidade_cobranca: Mapped[UnidadeCobrancaServico] = mapped_column(
        SAEnum(UnidadeCobrancaServico, name="unidade_cobranca_servico"), nullable=False
    )
    preco: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    requer_visita_tecnica: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    disponibilidade: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

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
