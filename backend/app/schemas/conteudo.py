"""Schemas — ConteudoEducativo, PreferenciaComunicacao, Dispositivo."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

from app.models.enums import ConteudoTipo
from app.schemas.common import TimestampedORM


# === ConteudoEducativo ===

class ConteudoEducativoBase(BaseModel):
    titulo: Annotated[str, StringConstraints(min_length=3, max_length=200)]
    resumo: str | None = None
    tipo: ConteudoTipo
    papeis_alvo: list[str] = Field(default_factory=list)
    categorias_alvo: list[str] = Field(default_factory=list)
    url: str | None = None
    conteudo: str | None = None
    capa_path: str | None = None
    publicado: bool = False


class ConteudoEducativoCreate(ConteudoEducativoBase): ...


class ConteudoEducativoUpdate(BaseModel):
    titulo: str | None = None
    resumo: str | None = None
    papeis_alvo: list[str] | None = None
    categorias_alvo: list[str] | None = None
    url: str | None = None
    conteudo: str | None = None
    publicado: bool | None = None


class ConteudoEducativoRead(ConteudoEducativoBase, TimestampedORM): ...


# === PreferenciaComunicacao ===

class PreferenciaComunicacaoUpdate(BaseModel):
    aceita_alerta_pago_de_terceiros: bool | None = None
    aceita_comunicacao_prefeitura_municipio: bool | None = None
    aceita_comunicacao_orgao_estadual: bool | None = None
    aceita_novidades_plataforma: bool | None = None
    aceita_conteudo_educativo: bool | None = None


class PreferenciaComunicacaoRead(TimestampedORM):
    conta_id: UUID
    aceita_alerta_pago_de_terceiros: bool
    aceita_comunicacao_prefeitura_municipio: bool
    aceita_comunicacao_orgao_estadual: bool
    aceita_novidades_plataforma: bool
    aceita_conteudo_educativo: bool


# === Dispositivo (push) ===

class DispositivoRegister(BaseModel):
    plataforma: Annotated[str, StringConstraints(pattern=r"^(ios|android|web)$")]
    token: Annotated[str, StringConstraints(min_length=10, max_length=255)]
    modelo: str | None = None
    versao_app: str | None = None


class DispositivoRead(TimestampedORM):
    usuario_id: UUID
    plataforma: str
    token: str
    modelo: str | None
    versao_app: str | None
    ativo: bool


# === Comunicação segmentada (admin) ===

class ComunicacaoDispararRequest(BaseModel):
    titulo: Annotated[str, StringConstraints(min_length=3, max_length=200)]
    corpo: Annotated[str, StringConstraints(min_length=10, max_length=1000)]
    finalidade: Annotated[
        str,
        StringConstraints(
            pattern=r"^(novidades_plataforma|conteudo_educativo|comunicacao_prefeitura_municipio|comunicacao_orgao_estadual)$"
        ),
    ]
    segmentacao: dict = Field(default_factory=dict)
