"""ConviteMembro — convite de admin para adicionar Membro à Conta PJ.

Expira em 48h; segundo convite para o mesmo e-mail substitui o anterior.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import ConviteStatus, PapelInternoMembro

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.usuario import Usuario


class ConviteMembro(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "convite_membro"

    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    papel_interno: Mapped[PapelInternoMembro] = mapped_column(
        SAEnum(PapelInternoMembro, name="papel_interno_membro", create_type=False),
        default=PapelInternoMembro.OPERADOR,
        nullable=False,
    )

    token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[ConviteStatus] = mapped_column(
        SAEnum(ConviteStatus, name="convite_status"), default=ConviteStatus.PENDENTE, nullable=False
    )

    convidado_por_usuario_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False
    )
    aceito_por_usuario_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True
    )

    conta: Mapped["Conta"] = relationship("Conta")
    convidado_por: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[convidado_por_usuario_id])
