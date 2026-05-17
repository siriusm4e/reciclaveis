"""ConteudoEducativo — artigo, dica, curso ou vídeo segmentado por Papel/Categoria."""

from __future__ import annotations

from sqlalchemy import Boolean, Enum as SAEnum, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import ConteudoTipo


class ConteudoEducativo(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "conteudo_educativo"

    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    resumo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tipo: Mapped[ConteudoTipo] = mapped_column(
        SAEnum(ConteudoTipo, name="conteudo_tipo"), nullable=False, index=True
    )

    # Segmentação (slugs); listas vazias = público geral
    papeis_alvo: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    categorias_alvo: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)

    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    conteudo: Mapped[str | None] = mapped_column(Text, nullable=True)  # markdown (sanitizado)
    capa_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    publicado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
