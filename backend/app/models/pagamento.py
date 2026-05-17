"""Pagamento — tentativa de quitação de uma Fatura via gateway externo."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import PagamentoMetodo, PagamentoStatus

if TYPE_CHECKING:
    from app.models.fatura import Fatura


class Pagamento(Base, UUIDPKMixin, TimestampMixin):
    fatura_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("fatura.id", ondelete="CASCADE"), nullable=False, index=True
    )
    valor_centavos: Mapped[int] = mapped_column(Integer, nullable=False)
    metodo: Mapped[PagamentoMetodo] = mapped_column(
        SAEnum(PagamentoMetodo, name="pagamento_metodo"), nullable=False
    )
    status: Mapped[PagamentoStatus] = mapped_column(
        SAEnum(PagamentoStatus, name="pagamento_status"),
        default=PagamentoStatus.PENDENTE,
        nullable=False,
        index=True,
    )
    tentativa: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    gateway_id: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    mensagem_gateway: Mapped[str | None] = mapped_column(String(500), nullable=True)

    fatura: Mapped["Fatura"] = relationship("Fatura", back_populates="pagamentos")
