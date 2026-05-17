"""Usuario — pessoa física com login. Distinto da Conta (ver M01)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.membro import Membro
    from app.models.perfil_interno import PerfilInterno


class Usuario(Base, UUIDPKMixin, TimestampMixin):
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email_confirmado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    nome_completo: Mapped[str] = mapped_column(String(255), nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    foto_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # MFA TOTP
    mfa_ativo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Anti-bruteforce
    login_falhos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bloqueado_ate: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # LGPD — pedido de exclusão, processado após graça (30 dias)
    pedido_exclusao_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    memberships: Mapped[list["Membro"]] = relationship(
        "Membro", back_populates="usuario", cascade="all, delete-orphan"
    )
    perfil_interno: Mapped["PerfilInterno | None"] = relationship(
        "PerfilInterno", back_populates="usuario", uselist=False
    )
