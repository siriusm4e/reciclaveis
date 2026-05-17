"""Denuncia — reclamação aberta pelo usuário contra Publicação/Conta/Mensagem."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SAEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import DenunciaAlvoTipo, DenunciaStatus, DenunciaTipoFechado

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.decisao_moderacao import DecisaoModeracao


class Denuncia(Base, UUIDPKMixin, TimestampMixin):
    denunciante_conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )

    alvo_tipo: Mapped[DenunciaAlvoTipo] = mapped_column(
        SAEnum(DenunciaAlvoTipo, name="denuncia_alvo_tipo"), nullable=False, index=True
    )
    alvo_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)

    tipo_fechado: Mapped[DenunciaTipoFechado] = mapped_column(
        SAEnum(DenunciaTipoFechado, name="denuncia_tipo_fechado"), nullable=False
    )
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[DenunciaStatus] = mapped_column(
        SAEnum(DenunciaStatus, name="denuncia_status"),
        default=DenunciaStatus.ABERTA,
        nullable=False,
        index=True,
    )

    denunciante: Mapped["Conta"] = relationship("Conta")
    decisoes: Mapped[list["DecisaoModeracao"]] = relationship(
        "DecisaoModeracao", back_populates="denuncia", cascade="all, delete-orphan"
    )
