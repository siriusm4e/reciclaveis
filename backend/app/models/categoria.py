"""Categoria de material reciclável (Metais, Plásticos, Papéis, ...).

Topo da taxonomia: Categoria → Subcategoria (intermediário) → TipoMaterial (granular).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.subcategoria import Subcategoria


class Categoria(Base, UUIDPKMixin, TimestampMixin):
    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    cor_hex: Mapped[str] = mapped_column(String(7), nullable=False)  # "#1e8c4e"
    icone: Mapped[str] = mapped_column(String(60), nullable=False)   # nome lucide-react
    ordem: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    subcategorias: Mapped[list["Subcategoria"]] = relationship(
        "Subcategoria", back_populates="categoria", cascade="all, delete-orphan"
    )
