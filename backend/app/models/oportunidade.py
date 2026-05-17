"""Oportunidade — licitação, concorrência, chamada pública/privada (M04)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import OportunidadeStatus, OportunidadeTipo

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.proposta import Proposta
    from app.models.subcategoria import Subcategoria


class Oportunidade(Base, UUIDPKMixin, TimestampMixin):
    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    subcategoria_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("subcategoria.id"), nullable=False, index=True
    )

    tipo: Mapped[OportunidadeTipo] = mapped_column(
        SAEnum(OportunidadeTipo, name="oportunidade_tipo"), nullable=False, index=True
    )
    # Lista de slugs de TipoDocumento exigidos para submeter Proposta
    documentos_exigidos: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    prazo_submissao: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    valor_estimado: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)

    status: Mapped[OportunidadeStatus] = mapped_column(
        SAEnum(OportunidadeStatus, name="oportunidade_status"),
        default=OportunidadeStatus.ABERTA_PARA_PROPOSTA,
        nullable=False,
        index=True,
    )
    proposta_vencedora_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("proposta.id", use_alter=True), nullable=True
    )

    conta: Mapped["Conta"] = relationship("Conta")
    subcategoria: Mapped["Subcategoria"] = relationship("Subcategoria")
    propostas: Mapped[list["Proposta"]] = relationship(
        "Proposta",
        back_populates="oportunidade",
        foreign_keys="Proposta.oportunidade_id",
        cascade="all, delete-orphan",
    )
