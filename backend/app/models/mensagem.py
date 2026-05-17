"""Mensagem — entrada do chat de Negociação."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SAEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import MensagemTipo

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.negociacao import Negociacao
    from app.models.usuario import Usuario


class Mensagem(Base, UUIDPKMixin, TimestampMixin):
    negociacao_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("negociacao.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    conta_remetente_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id"), nullable=False, index=True
    )
    # NULL para mensagens do sistema (status_alterado, aceite, etc.)
    usuario_remetente_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True
    )

    conteudo: Mapped[str] = mapped_column(Text, nullable=False)  # já sanitizado (bleach) no service
    tipo: Mapped[MensagemTipo] = mapped_column(
        SAEnum(MensagemTipo, name="mensagem_tipo"),
        default=MensagemTipo.TEXTO,
        nullable=False,
    )

    negociacao: Mapped["Negociacao"] = relationship("Negociacao", back_populates="mensagens")
    conta_remetente: Mapped["Conta"] = relationship("Conta")
    usuario_remetente: Mapped["Usuario | None"] = relationship("Usuario")
