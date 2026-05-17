"""Assinatura — vínculo Conta + Papel + Plano com ciclo de vida."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import AssinaturaStatus

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.fatura import Fatura
    from app.models.papel import PapelAtivado
    from app.models.plano import Plano


class Assinatura(Base, UUIDPKMixin, TimestampMixin):
    __table_args__ = (
        UniqueConstraint("conta_id", "papel_id", name="uq_assinatura_conta_papel"),
    )

    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    papel_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("papel_ativado.id", ondelete="CASCADE"), nullable=False
    )
    plano_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("plano.id"), nullable=False
    )

    status: Mapped[AssinaturaStatus] = mapped_column(
        SAEnum(AssinaturaStatus, name="assinatura_status"),
        default=AssinaturaStatus.ATIVA,
        nullable=False,
        index=True,
    )
    data_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_renovacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    em_graca_desde: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pausada_desde: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ciclo_cortesia: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    conta: Mapped["Conta"] = relationship("Conta")
    papel: Mapped["PapelAtivado"] = relationship("PapelAtivado")
    plano: Mapped["Plano"] = relationship("Plano")
    faturas: Mapped[list["Fatura"]] = relationship(
        "Fatura", back_populates="assinatura", cascade="all, delete-orphan"
    )
