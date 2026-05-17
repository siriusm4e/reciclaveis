"""AnuncioMaquina — equipamento à venda/aluguel (qualquer Conta pode publicar)."""

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
from app.models.enums import AnuncioStatus, CondicaoEquipamento, ModalidadeMaquina

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.papel import PapelAtivado


class AnuncioMaquina(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "anuncio_maquina"
    __table_args__ = (
        Index("ix_anuncio_maquina_geom_gist", "geom", postgresql_using="gist"),
    )

    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    papel_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("papel_ativado.id"), nullable=True
    )

    categoria_equipamento: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    marca: Mapped[str | None] = mapped_column(String(80), nullable=True)
    modelo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ano: Mapped[int | None] = mapped_column(Integer, nullable=True)
    capacidade: Mapped[str | None] = mapped_column(String(80), nullable=True)
    tensao: Mapped[str | None] = mapped_column(String(40), nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    condicao: Mapped[CondicaoEquipamento] = mapped_column(
        SAEnum(CondicaoEquipamento, name="condicao_equipamento"), nullable=False
    )
    modalidade: Mapped[ModalidadeMaquina] = mapped_column(
        SAEnum(ModalidadeMaquina, name="modalidade_maquina"), nullable=False, index=True
    )

    # Para aluguel
    aceita_visita_tecnica: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    disponibilidade: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    preco: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    documentacao_disponivel: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fotos: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    # Local DO EQUIPAMENTO (não da Conta — define busca espacial)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    geom: Mapped[object] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )

    prazo_validade: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[AnuncioStatus] = mapped_column(
        SAEnum(AnuncioStatus, name="anuncio_status"),
        default=AnuncioStatus.RASCUNHO,
        nullable=False,
        index=True,
    )

    conta: Mapped["Conta"] = relationship("Conta")
    papel: Mapped["PapelAtivado | None"] = relationship("PapelAtivado")
