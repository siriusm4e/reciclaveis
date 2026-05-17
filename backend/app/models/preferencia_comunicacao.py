"""PreferenciaComunicacao — opt-ins granulares por finalidade (LGPD by design)."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.conta import Conta


class PreferenciaComunicacao(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "preferencia_comunicacao"

    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("conta.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Aceita receber push de Alerta Pago de outras Contas (filtro de receptor)
    aceita_alerta_pago_de_terceiros: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Comunicação institucional
    aceita_comunicacao_prefeitura_municipio: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    aceita_comunicacao_orgao_estadual: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Marketing e conteúdo
    aceita_novidades_plataforma: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    aceita_conteudo_educativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    conta: Mapped["Conta"] = relationship("Conta", back_populates="preferencias")
