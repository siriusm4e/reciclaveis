"""PacoteCredito — SKU de Créditos comercializado (compra à vista)."""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class PacoteCredito(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "pacote_credito"

    nome: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    creditos: Mapped[int] = mapped_column(Integer, nullable=False)
    bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    preco_centavos: Mapped[int] = mapped_column(Integer, nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
