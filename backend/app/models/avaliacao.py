"""Avaliacao — reputação por Papel, com janela cega de 14 dias.

`visivel=false` até reciprocidade OU 14 dias decorridos (Celery task).
Não é gerada se houver VinculoDetectado entre as Contas.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import PapelTipo

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.negociacao import Negociacao


class Avaliacao(Base, UUIDPKMixin, TimestampMixin):
    __table_args__ = (
        CheckConstraint("nota BETWEEN 1 AND 5", name="ck_avaliacao_nota_range"),
        # Cada Conta avalia a contraparte UMA vez por Negociação
        UniqueConstraint(
            "negociacao_id", "avaliador_conta_id", name="uq_avaliacao_negociacao_avaliador"
        ),
    )

    negociacao_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("negociacao.id", ondelete="CASCADE"), nullable=False, index=True
    )
    avaliador_conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id"), nullable=False, index=True
    )
    avaliado_conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id"), nullable=False, index=True
    )
    papel_avaliado: Mapped[PapelTipo] = mapped_column(
        SAEnum(PapelTipo, name="papel_tipo", create_type=False),
        nullable=False,
        index=True,
    )

    nota: Mapped[int] = mapped_column(Integer, nullable=False)
    # Sub-notas opcionais: pontualidade, comunicação, qualidade, etc.
    subnotas: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)

    visivel: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    # True se removida por moderador (com motivo em DecisaoModeracao)
    removida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    negociacao: Mapped["Negociacao"] = relationship("Negociacao", back_populates="avaliacoes")
    avaliador: Mapped["Conta"] = relationship("Conta", foreign_keys=[avaliador_conta_id])
    avaliado: Mapped["Conta"] = relationship("Conta", foreign_keys=[avaliado_conta_id])
