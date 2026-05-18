"""Subcategoria — nível intermediário da taxonomia.

Hierarquia:
    Categoria (ex: Plásticos)
      → Subcategoria (ex: PET)            ← este model
          → TipoMaterial (ex: PET cristal)

Regulação documental (Hospitalar, Químicos) vive aqui — todos os TiposMaterial
dependentes herdam a exigência via `requer_validacao_documental` da Subcategoria.

Atributos específicos (cor, granulometria, etc.) ficam em TipoMaterial.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.categoria import Categoria
    from app.models.tipo_material import TipoMaterial


class Subcategoria(Base, UUIDPKMixin, TimestampMixin):
    __table_args__ = (
        UniqueConstraint("categoria_id", "slug", name="uq_subcategoria_categoria_slug"),
    )

    categoria_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("categoria.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False)

    # Regulação documental — flag e lista de documentos exigidos vivem no
    # nível intermediário (ex.: toda Hospitalar > Infectantes exige licença).
    requer_validacao_documental: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    documentos_exigidos: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    ordem: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    categoria: Mapped["Categoria"] = relationship("Categoria", back_populates="subcategorias")
    tipos_material: Mapped[list["TipoMaterial"]] = relationship(
        "TipoMaterial", back_populates="subcategoria", cascade="all, delete-orphan"
    )
