"""VinculoDetectado — laço suspeito entre duas Contas que bloqueia avaliações recíprocas."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import VinculoMotivo

if TYPE_CHECKING:
    from app.models.conta import Conta


class VinculoDetectado(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "vinculo_detectado"
    __table_args__ = (
        UniqueConstraint(
            "conta_a_id", "conta_b_id", "motivo", name="uq_vinculo_detectado_par_motivo"
        ),
    )

    conta_a_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    conta_b_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    motivo: Mapped[VinculoMotivo] = mapped_column(
        SAEnum(VinculoMotivo, name="vinculo_motivo"), nullable=False
    )

    conta_a: Mapped["Conta"] = relationship("Conta", foreign_keys=[conta_a_id])
    conta_b: Mapped["Conta"] = relationship("Conta", foreign_keys=[conta_b_id])
