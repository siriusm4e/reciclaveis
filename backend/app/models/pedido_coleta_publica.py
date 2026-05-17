"""PedidoColetaPublica — solicitação cidadã roteada para a Prefeitura do bairro."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from geoalchemy2 import Geometry
from sqlalchemy import Enum as SAEnum, Float, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import PedidoColetaStatus

if TYPE_CHECKING:
    from app.models.conta import Conta


class PedidoColetaPublica(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "pedido_coleta_publica"
    __table_args__ = (
        Index("ix_pedido_coleta_geom_gist", "geom", postgresql_using="gist"),
    )

    conta_solicitante_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Roteamento: prefeitura responsável pelo bairro (se não houver, fica em aguardando_municipio)
    prefeitura_conta_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id"), nullable=True, index=True
    )

    bairro: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    uf: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    ibge_municipio: Mapped[str | None] = mapped_column(String(7), nullable=True, index=True)

    tipo_residuo: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    foto_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    quantidade_estimada: Mapped[Numeric | None] = mapped_column(Numeric(10, 2), nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    geom: Mapped[object] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )

    status: Mapped[PedidoColetaStatus] = mapped_column(
        SAEnum(PedidoColetaStatus, name="pedido_coleta_status"),
        default=PedidoColetaStatus.ABERTA,
        nullable=False,
        index=True,
    )

    conta_solicitante: Mapped["Conta"] = relationship("Conta", foreign_keys=[conta_solicitante_id])
    prefeitura: Mapped["Conta | None"] = relationship("Conta", foreign_keys=[prefeitura_conta_id])
