"""PapelAtivado — papel funcional ativo na Conta (catador, comprador, freteiro, etc).

Papel é da Conta, não do Usuário. Uma Conta pode ter N papéis simultâneos.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import PapelStatus, PapelTipo

if TYPE_CHECKING:
    from app.models.conta import Conta


class PapelAtivado(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "papel_ativado"
    __table_args__ = (UniqueConstraint("conta_id", "papel", name="uq_papel_conta_papel"),)

    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    papel: Mapped[PapelTipo] = mapped_column(
        SAEnum(PapelTipo, name="papel_tipo"), nullable=False, index=True
    )
    status: Mapped[PapelStatus] = mapped_column(
        SAEnum(PapelStatus, name="papel_status"), default=PapelStatus.PENDENTE, nullable=False
    )

    # Dados específicos do papel (volume mensal, tipo de carga, frota, etc.)
    dados_complementares: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    conta: Mapped["Conta"] = relationship("Conta", back_populates="papeis")
