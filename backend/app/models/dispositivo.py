"""Dispositivo — token push (FCM Android / APNs iOS) por Usuario."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Dispositivo(Base, UUIDPKMixin, TimestampMixin):
    __table_args__ = (
        UniqueConstraint("token", name="uq_dispositivo_token"),
    )

    usuario_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plataforma: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # ios|android|web
    token: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    modelo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    versao_app: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    usuario: Mapped["Usuario"] = relationship("Usuario")
