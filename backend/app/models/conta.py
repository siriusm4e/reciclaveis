"""Conta — entidade que opera no marketplace (PF, PJ-Privada ou Órgão Público).

Tipo imutável após criação (ver M01).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum as SAEnum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import ContaStatus, ContaTipo

# Re-export para outros módulos importarem como `from app.models.conta import ContaStatus`
__all__ = ["Conta", "ContaStatus", "ContaTipo"]

if TYPE_CHECKING:
    from app.models.estabelecimento import Estabelecimento
    from app.models.membro import Membro
    from app.models.papel import PapelAtivado
    from app.models.preferencia_comunicacao import PreferenciaComunicacao


class Conta(Base, UUIDPKMixin, TimestampMixin):
    tipo: Mapped[ContaTipo] = mapped_column(
        SAEnum(ContaTipo, name="conta_tipo"), nullable=False, index=True
    )
    status: Mapped[ContaStatus] = mapped_column(
        SAEnum(ContaStatus, name="conta_status"),
        default=ContaStatus.PENDENTE,
        nullable=False,
        index=True,
    )

    # PF: nome_publico = nome_completo do usuário. PJ: razão social ou nome fantasia.
    nome_publico: Mapped[str] = mapped_column(String(255), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(14), unique=True, nullable=True, index=True)
    # Para PF a chave CPF vive no Usuario (admin único da Conta).
    foto_perfil_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Para Conta Órgão Público: escopo territorial (municipio / estado)
    # ex.: {"escopo": "municipio", "uf": "SP", "ibge": "3550308"}
    escopo_territorial: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Cortesia de assinatura: bypass de cobrança autorizada por admin
    cortesia_ativa: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relacionamentos
    membros: Mapped[list["Membro"]] = relationship(
        "Membro", back_populates="conta", cascade="all, delete-orphan"
    )
    papeis: Mapped[list["PapelAtivado"]] = relationship(
        "PapelAtivado", back_populates="conta", cascade="all, delete-orphan"
    )
    estabelecimentos: Mapped[list["Estabelecimento"]] = relationship(
        "Estabelecimento", back_populates="conta", cascade="all, delete-orphan"
    )
    preferencias: Mapped["PreferenciaComunicacao | None"] = relationship(
        "PreferenciaComunicacao", back_populates="conta", uselist=False, cascade="all, delete-orphan"
    )
