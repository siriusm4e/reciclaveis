"""AuditLog — registro imutável (INSERT only) de ações sensíveis.

Retenção: 5 anos (configurável em settings.AUDIT_LOG_RETENCAO_ANOS).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class AuditLog(Base, UUIDPKMixin):
    """Sem updated_at — tabela INSERT only por design."""

    __tablename__ = "audit_log"

    # Quem fez (Usuario interno: admin operando o backoffice; Usuario externo: cliente)
    admin_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True, index=True
    )
    usuario_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True, index=True
    )

    # O que: namespace.acao (ex.: "conta.aprovar", "documento.rejeitar")
    acao: Mapped[str] = mapped_column(String(120), nullable=False, index=True)

    # Sobre o quê
    recurso_tipo: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    recurso_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)

    # Conta afetada (para suspensão, anonimização, etc.)
    conta_afetada_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id"), nullable=True, index=True
    )

    # Diff / payload / justificativa
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    motivo: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Contexto técnico
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    admin: Mapped["Usuario | None"] = relationship("Usuario", foreign_keys=[admin_id])
    usuario: Mapped["Usuario | None"] = relationship("Usuario", foreign_keys=[usuario_id])
