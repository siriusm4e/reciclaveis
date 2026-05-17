"""TransacaoCredito — ledger imutável de Créditos por Conta.

Regras absolutas:
- INSERT only. Ajustes via nova transação tipo=ajuste_admin (com admin_id e motivo).
- Saldo = SUM(valor) WHERE conta_id=X (projeção, nunca campo direto).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import TransacaoTipo

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.usuario import Usuario


class TransacaoCredito(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "transacao_credito"

    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[TransacaoTipo] = mapped_column(
        SAEnum(TransacaoTipo, name="transacao_tipo"), nullable=False, index=True
    )
    # Positivo (compra, reembolso, ajuste_admin+, bônus) ou negativo (consumo, ajuste_admin-)
    valor: Mapped[int] = mapped_column(Integer, nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)

    # Referência polimórfica (OfertaCompra para consumo de boost, PacoteCredito para compra, ...)
    referencia_tipo: Mapped[str | None] = mapped_column(String(60), nullable=True)
    referencia_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)

    # Obrigatório para tipo=ajuste_admin
    admin_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True
    )

    conta: Mapped["Conta"] = relationship("Conta")
    admin: Mapped["Usuario | None"] = relationship("Usuario")
