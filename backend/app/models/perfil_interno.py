"""PerfilInterno — vínculo de Usuario ao backoffice com matriz de permissão (M16)."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import PerfilInternoTipo

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class PerfilInterno(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "perfil_interno"
    __table_args__ = (
        UniqueConstraint("usuario_id", name="uq_perfil_interno_usuario"),
    )

    usuario_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[PerfilInternoTipo] = mapped_column(
        SAEnum(PerfilInternoTipo, name="perfil_interno_tipo"), nullable=False, index=True
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="perfil_interno")


class PermissaoBackoffice(Base, UUIDPKMixin, TimestampMixin):
    """Matriz `perfil × recurso × acao` editável sem redeploy (regra M16)."""

    __tablename__ = "permissao_backoffice"
    __table_args__ = (
        UniqueConstraint(
            "perfil", "recurso", "acao", name="uq_permissao_perfil_recurso_acao"
        ),
    )

    perfil: Mapped[PerfilInternoTipo] = mapped_column(
        SAEnum(PerfilInternoTipo, name="perfil_interno_tipo", create_type=False), nullable=False, index=True
    )
    recurso: Mapped[str] = mapped_column(String(60), nullable=False)  # ex.: "fatura", "denuncia"
    acao: Mapped[str] = mapped_column(String(40), nullable=False)     # ex.: "ler", "atualizar", "excluir"
    permitido: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
