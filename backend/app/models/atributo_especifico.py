"""AtributoComum — catálogo dos atributos compartilhados entre todos TiposMaterial.

São fixos do schema (peso, unidade_venda, estado, limpeza, forma_apresentacao,
origem, frequência). Os AtributosEspecíficos por TipoMaterial vivem no JSONB
de `TipoMaterial.atributos_especificos`.

Esta tabela serve como dicionário de referência editável pelo admin (rótulos,
ajuda contextual), sem alterar o schema do banco.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class AtributoComum(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "atributo_comum"

    chave: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # string|number|enum|bool
    enum_valores: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    ajuda: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ordem: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
