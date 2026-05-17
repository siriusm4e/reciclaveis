"""AssinaturaAlerta — assinatura gratuita de alertas por filtro (não confundir com Plano)."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.categoria import Categoria
    from app.models.conta import Conta
    from app.models.papel import PapelAtivado


class AssinaturaAlerta(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "assinatura_alerta"

    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    papel_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("papel_ativado.id"), nullable=False
    )
    categoria_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("categoria.id"), nullable=False, index=True
    )
    # Lista de UUID de Subcategorias (string para evitar array de FK em JSONB)
    subcategoria_ids: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    raio_km: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_min: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    conta: Mapped["Conta"] = relationship("Conta")
    papel: Mapped["PapelAtivado"] = relationship("PapelAtivado")
    categoria: Mapped["Categoria"] = relationship("Categoria")
