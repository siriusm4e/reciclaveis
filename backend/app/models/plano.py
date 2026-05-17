"""Plano — pacote de assinatura mensal por Papel."""

from __future__ import annotations

from sqlalchemy import Boolean, Enum as SAEnum, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import PapelTipo


class Plano(Base, UUIDPKMixin, TimestampMixin):
    __table_args__ = (UniqueConstraint("papel", "nome", name="uq_plano_papel_nome"),)

    papel: Mapped[PapelTipo] = mapped_column(
        SAEnum(PapelTipo, name="papel_tipo", create_type=False), nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(String(80), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(500), nullable=True)
    limite_publicacoes_ativas: Mapped[int] = mapped_column(Integer, nullable=False)
    permite_alerta_pago: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    preco_mensal_centavos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    gratuito: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
