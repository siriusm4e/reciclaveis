"""Proposta — submissão a uma Oportunidade. Entidade autônoma (não vira Negociação)."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SAEnum, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import PropostaStatus

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.oportunidade import Oportunidade


class Proposta(Base, UUIDPKMixin, TimestampMixin):
    oportunidade_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("oportunidade.id", ondelete="CASCADE"), nullable=False, index=True
    )
    conta_proponente_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )

    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    condicoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Lista de paths para documentos anexos validados separadamente
    documentos_anexos: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    status: Mapped[PropostaStatus] = mapped_column(
        SAEnum(PropostaStatus, name="proposta_status"),
        default=PropostaStatus.SUBMETIDA,
        nullable=False,
        index=True,
    )

    oportunidade: Mapped["Oportunidade"] = relationship(
        "Oportunidade", back_populates="propostas", foreign_keys=[oportunidade_id]
    )
    conta_proponente: Mapped["Conta"] = relationship("Conta")
