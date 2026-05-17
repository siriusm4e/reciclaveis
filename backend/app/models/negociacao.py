"""Negociacao — conversa estruturada entre duas Contas sobre uma Publicação.

A Negociação é o único container do chat. Nenhum chat existe fora dela.
Múltiplas Negociações simultâneas sobre o mesmo Anúncio são permitidas
(uma por contraparte).

Quem é vendedor e quem é comprador depende do tipo de publicação:
- AnuncioVenda → conta criadora = vendedora; contraparte interessada = compradora.
- OfertaCompra → conta criadora = compradora; contraparte que aceita = vendedora.
- AnuncioMaquina/Servico/Frete → conta criadora = ofertante; contraparte = cliente.

`aceite_localizacao_exata` bilateral libera lat_real no endpoint de Negociação.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import MotivoCancelamento, NegociacaoStatus, PublicacaoTipo

if TYPE_CHECKING:
    from app.models.avaliacao import Avaliacao
    from app.models.conta import Conta
    from app.models.mensagem import Mensagem


class Negociacao(Base, UUIDPKMixin, TimestampMixin):
    __table_args__ = (
        # Evita duas Negociações abertas entre o mesmo par sobre a mesma publicação
        UniqueConstraint(
            "publicacao_id",
            "publicacao_tipo",
            "conta_vendedora_id",
            "conta_compradora_id",
            name="uq_negociacao_par_publicacao",
        ),
    )

    publicacao_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    publicacao_tipo: Mapped[PublicacaoTipo] = mapped_column(
        SAEnum(PublicacaoTipo, name="publicacao_tipo"), nullable=False, index=True
    )

    conta_vendedora_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )
    conta_compradora_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[NegociacaoStatus] = mapped_column(
        SAEnum(NegociacaoStatus, name="negociacao_status"),
        default=NegociacaoStatus.ABERTA,
        nullable=False,
        index=True,
    )

    # Confirmação bilateral de localização exata
    aceite_localizacao_exata_vendedor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    aceite_localizacao_exata_comprador: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Sinalização de "combinado" — inicia contador de 48h
    sinalizou_combinado_vendedor_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sinalizou_combinado_comprador_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    combinada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Cancelamento
    motivo_cancelamento: Mapped[MotivoCancelamento | None] = mapped_column(
        SAEnum(MotivoCancelamento, name="motivo_cancelamento"), nullable=True
    )
    motivo_cancelamento_texto: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancelada_por_conta_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("conta.id"), nullable=True
    )
    cancelada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Audit trail granular (cada transição com timestamp, conta, IP)
    audit_trail: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    # Atalho para ordenação de feed
    ultima_mensagem_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    ultima_mensagem_preview: Mapped[str | None] = mapped_column(String(255), nullable=True)

    conta_vendedora: Mapped["Conta"] = relationship("Conta", foreign_keys=[conta_vendedora_id])
    conta_compradora: Mapped["Conta"] = relationship("Conta", foreign_keys=[conta_compradora_id])
    mensagens: Mapped[list["Mensagem"]] = relationship(
        "Mensagem", back_populates="negociacao", cascade="all, delete-orphan", order_by="Mensagem.created_at"
    )
    avaliacoes: Mapped[list["Avaliacao"]] = relationship(
        "Avaliacao", back_populates="negociacao", cascade="all, delete-orphan"
    )
