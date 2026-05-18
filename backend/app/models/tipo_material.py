"""TipoMaterial — nível mais granular da taxonomia (era `subcategoria`).

Hierarquia:
    Categoria (ex: Plásticos)
      → Subcategoria (ex: PET)
          → TipoMaterial (ex: PET cristal)   ← este model

Atributos específicos (cor, granulometria, prensagem, etc.) vivem aqui em
`atributos_especificos` (schema JSON). Regulação documental fica no nível
da Subcategoria — TipoMaterial herda comportamento via `subcategoria.requer_validacao_documental`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.subcategoria import Subcategoria


class TipoMaterial(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "tipo_material"
    __table_args__ = (
        UniqueConstraint("subcategoria_id", "slug", name="uq_tipo_material_subcategoria_slug"),
    )

    subcategoria_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("subcategoria.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False)
    unidade_padrao: Mapped[str] = mapped_column(String(20), nullable=False)  # kg, ton, m3, unidade, l

    # Schema JSON dos atributos específicos do tipo.
    # Estrutura: {"campo": {"type": "string|number|enum|bool", "label": "...", "enum": [...]}}
    atributos_especificos: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    ordem: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    subcategoria: Mapped["Subcategoria"] = relationship(
        "Subcategoria", back_populates="tipos_material"
    )
