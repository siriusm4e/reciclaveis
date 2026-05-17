"""Estabelecimento — endereço operacional físico de Conta PJ."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.conta import Conta


class Estabelecimento(Base, UUIDPKMixin, TimestampMixin):
    __table_args__ = (
        # Índice GIST obrigatório em todas as colunas geoespaciais (regra absoluta)
        Index(
            "ix_estabelecimento_geom_gist",
            "geom",
            postgresql_using="gist",
        ),
    )

    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )

    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    cep: Mapped[str] = mapped_column(String(8), nullable=False)
    logradouro: Mapped[str] = mapped_column(String(255), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    complemento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bairro: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    uf: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    ibge_municipio: Mapped[str | None] = mapped_column(String(7), nullable=True, index=True)

    geom: Mapped[object] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )

    conta: Mapped["Conta"] = relationship("Conta", back_populates="estabelecimentos")
