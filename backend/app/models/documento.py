"""Documento — instância de TipoDocumento submetida pela Conta.

`substitui_id` aponta para a instância anterior na cadeia de renovação.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import DocumentoStatus

if TYPE_CHECKING:
    from app.models.conta import Conta
    from app.models.estabelecimento import Estabelecimento
    from app.models.tipo_documento import TipoDocumento


class Documento(Base, UUIDPKMixin, TimestampMixin):
    conta_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    estabelecimento_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("estabelecimento.id", ondelete="CASCADE"), nullable=True, index=True
    )
    tipo_documento_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tipo_documento.id"), nullable=False, index=True
    )

    numero: Mapped[str | None] = mapped_column(String(80), nullable=True)
    data_emissao: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_vencimento: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

    arquivo_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime: Mapped[str] = mapped_column(String(80), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(nullable=False, default=0)

    status: Mapped[DocumentoStatus] = mapped_column(
        SAEnum(DocumentoStatus, name="documento_status"),
        default=DocumentoStatus.PENDENTE,
        nullable=False,
        index=True,
    )

    # Cadeia de renovação: nova instância referencia a anterior
    substitui_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("documento.id"), nullable=True
    )

    aprovado_por_admin_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=True
    )
    motivo_rejeicao: Mapped[str | None] = mapped_column(String(500), nullable=True)

    conta: Mapped["Conta"] = relationship("Conta")
    estabelecimento: Mapped["Estabelecimento | None"] = relationship("Estabelecimento")
    tipo_documento: Mapped["TipoDocumento"] = relationship("TipoDocumento")
    substitui: Mapped["Documento | None"] = relationship("Documento", remote_side="Documento.id")
