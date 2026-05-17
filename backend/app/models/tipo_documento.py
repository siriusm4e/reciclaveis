"""TipoDocumento — catálogo administrável de documentos exigidos.

Escopo: `conta` (CNPJ, contrato social) ou `estabelecimento` (alvará, licença).
`exige_aprovacao_manual=True` impede aprovação automática (regra absoluta).
"""

from __future__ import annotations

from sqlalchemy import Boolean, Enum as SAEnum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import DocumentoEscopo


class TipoDocumento(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "tipo_documento"

    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(500), nullable=True)

    escopo: Mapped[DocumentoEscopo] = mapped_column(
        SAEnum(DocumentoEscopo, name="documento_escopo"), nullable=False, index=True
    )
    # Papéis (PapelTipo.value) aplicáveis. Lista vazia = qualquer papel.
    papeis_aplicaveis: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    tem_vencimento: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    exige_aprovacao_manual: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    obrigatorio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
