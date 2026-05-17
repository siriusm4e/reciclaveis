"""Schemas — Categoria, Subcategoria, AtributoComum."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

from app.schemas.common import ORMModel, TimestampedORM


# === Categoria ===

class CategoriaBase(BaseModel):
    nome: Annotated[str, StringConstraints(min_length=2, max_length=100)]
    slug: Annotated[str, StringConstraints(pattern=r"^[a-z0-9-]+$", max_length=100)]
    cor_hex: Annotated[str, StringConstraints(pattern=r"^#[0-9a-fA-F]{6}$")]
    icone: Annotated[str, StringConstraints(max_length=60)]
    ordem: int = 100
    ativo: bool = True


class CategoriaCreate(CategoriaBase): ...


class CategoriaUpdate(BaseModel):
    nome: str | None = None
    cor_hex: str | None = None
    icone: str | None = None
    ordem: int | None = None
    ativo: bool | None = None


class CategoriaRead(CategoriaBase, TimestampedORM): ...


# === Subcategoria ===

class SubcategoriaBase(BaseModel):
    categoria_id: UUID
    nome: Annotated[str, StringConstraints(min_length=2, max_length=150)]
    slug: Annotated[str, StringConstraints(pattern=r"^[a-z0-9-]+$", max_length=150)]
    unidade_padrao: Annotated[str, StringConstraints(max_length=20)]
    requer_validacao_documental: bool = False
    documentos_exigidos: list[str] = Field(default_factory=list)
    atributos_especificos: dict = Field(default_factory=dict)
    ordem: int = 100
    ativo: bool = True


class SubcategoriaCreate(SubcategoriaBase): ...


class SubcategoriaUpdate(BaseModel):
    nome: str | None = None
    unidade_padrao: str | None = None
    requer_validacao_documental: bool | None = None
    documentos_exigidos: list[str] | None = None
    atributos_especificos: dict | None = None
    ordem: int | None = None
    ativo: bool | None = None


class SubcategoriaRead(SubcategoriaBase, TimestampedORM): ...


# === AtributoComum (dicionário admin) ===

class AtributoComumBase(BaseModel):
    chave: Annotated[str, StringConstraints(pattern=r"^[a-z0-9_]+$", max_length=60)]
    label: Annotated[str, StringConstraints(max_length=120)]
    tipo: Annotated[str, StringConstraints(pattern=r"^(string|number|enum|bool)$")]
    enum_valores: list[str] | None = None
    ajuda: str | None = None
    ordem: int = 100
    ativo: bool = True


class AtributoComumCreate(AtributoComumBase): ...


class AtributoComumRead(AtributoComumBase, TimestampedORM): ...
