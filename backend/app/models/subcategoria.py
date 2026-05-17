"""Subcategoria — refinamento da Categoria, com schema JSONB de atributos específicos.

Subcategoria Regulada (`requer_validacao_documental=True`) bloqueia publicação
sem Documento aprovado do Tipo correspondente para o Papel do publicador.
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


class Subcategoria(Base, UUIDPKMixin, TimestampMixin):
    __table_args__ = (
        UniqueConstraint("categoria_id", "slug", name="uq_subcategoria_categoria_slug"),
    )

    categoria_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("categoria.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False)
    unidade_padrao: Mapped[str] = mapped_column(String(20), nullable=False)  # kg, ton, m3, unidade, ...

    # Subcategorias Reguladas exigem documentação específica (ex.: hospitalar, químicos)
    requer_validacao_documental: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Lista de slugs de TipoDocumento exigidos (ex.: ["licenca_ambiental", "cadri"])
    documentos_exigidos: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    # Schema JSON dos atributos específicos da Subcategoria.
    # Estrutura: {"campo": {"type": "string|number|enum|bool", "label": "...", "enum": [...]}}
    atributos_especificos: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    ordem: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    categoria: Mapped["Categoria"] = relationship("Categoria", back_populates="subcategorias")
