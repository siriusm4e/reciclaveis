"""Fatura — ciclo cobrado da Assinatura."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import FaturaStatus

if TYPE_CHECKING:
    from app.models.assinatura import Assinatura
    from app.models.pagamento import Pagamento


class Fatura(Base, UUIDPKMixin, TimestampMixin):
    assinatura_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("assinatura.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ciclo_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ciclo_fim: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    valor_centavos: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[FaturaStatus] = mapped_column(
        SAEnum(FaturaStatus, name="fatura_status"),
        default=FaturaStatus.PENDENTE,
        nullable=False,
        index=True,
    )
    vencimento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    assinatura: Mapped["Assinatura"] = relationship("Assinatura", back_populates="faturas")
    pagamentos: Mapped[list["Pagamento"]] = relationship(
        "Pagamento", back_populates="fatura", cascade="all, delete-orphan", order_by="Pagamento.tentativa"
    )
