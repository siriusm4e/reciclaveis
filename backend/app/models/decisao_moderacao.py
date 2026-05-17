"""DecisaoModeracao — ação tomada por moderador sobre uma Denúncia."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SAEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import AcaoModeracao

if TYPE_CHECKING:
    from app.models.denuncia import Denuncia
    from app.models.usuario import Usuario


class DecisaoModeracao(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "decisao_moderacao"

    denuncia_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("denuncia.id", ondelete="CASCADE"), nullable=False, index=True
    )
    admin_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False, index=True
    )
    acao: Mapped[AcaoModeracao] = mapped_column(
        SAEnum(AcaoModeracao, name="acao_moderacao"), nullable=False, index=True
    )
    motivo: Mapped[str] = mapped_column(Text, nullable=False)

    denuncia: Mapped["Denuncia"] = relationship("Denuncia", back_populates="decisoes")
    admin: Mapped["Usuario"] = relationship("Usuario")
