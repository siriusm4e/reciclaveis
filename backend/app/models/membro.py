"""Membro — vínculo Usuário ↔ Conta com papel interno (admin/operador/leitor)."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import PapelInternoMembro

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.usuario import Usuario


class Membro(Base, UUIDPKMixin, TimestampMixin):
    __table_args__ = (UniqueConstraint("usuario_id", "conta_id", name="uq_membro_usuario_conta"),)

    usuario_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, index=True
    )
    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    papel_interno: Mapped[PapelInternoMembro] = mapped_column(
        SAEnum(PapelInternoMembro, name="papel_interno_membro"),
        default=PapelInternoMembro.OPERADOR,
        nullable=False,
    )

    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="memberships")
    conta: Mapped["Conta"] = relationship("Conta", back_populates="membros")
