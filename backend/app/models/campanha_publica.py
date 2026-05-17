"""CampanhaPublica — campanha educativa/operacional de Prefeitura/Órgão Estadual."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import CampanhaStatus

if TYPE_CHECKING:
    from app.models.conta import Conta


class CampanhaPublica(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "campanha_publica"

    conta_organizadora_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )

    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    data_evento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    tipo_residuo: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    beneficio: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Escopo territorial: cidade ou estado (defaults para a Conta organizadora)
    cidade: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True, index=True)
    ibge_municipio: Mapped[str | None] = mapped_column(String(7), nullable=True, index=True)

    status: Mapped[CampanhaStatus] = mapped_column(
        SAEnum(CampanhaStatus, name="campanha_status"),
        default=CampanhaStatus.RASCUNHO,
        nullable=False,
        index=True,
    )

    conta_organizadora: Mapped["Conta"] = relationship("Conta")
