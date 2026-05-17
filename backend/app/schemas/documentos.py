"""Schemas — TipoDocumento e Documento."""

from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

from app.models.enums import DocumentoEscopo, DocumentoStatus
from app.schemas.common import TimestampedORM


# === TipoDocumento ===

class TipoDocumentoBase(BaseModel):
    slug: Annotated[str, StringConstraints(pattern=r"^[a-z0-9_]+$", max_length=80)]
    nome: Annotated[str, StringConstraints(min_length=2, max_length=150)]
    descricao: str | None = None
    escopo: DocumentoEscopo
    papeis_aplicaveis: list[str] = Field(default_factory=list)
    tem_vencimento: bool = False
    exige_aprovacao_manual: bool = True
    obrigatorio: bool = False
    ativo: bool = True


class TipoDocumentoCreate(TipoDocumentoBase): ...


class TipoDocumentoUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    papeis_aplicaveis: list[str] | None = None
    tem_vencimento: bool | None = None
    exige_aprovacao_manual: bool | None = None
    obrigatorio: bool | None = None
    ativo: bool | None = None


class TipoDocumentoRead(TipoDocumentoBase, TimestampedORM): ...


# === Documento ===

class DocumentoCreate(BaseModel):
    tipo_documento_id: UUID
    estabelecimento_id: UUID | None = None
    numero: str | None = None
    data_emissao: date | None = None
    data_vencimento: date | None = None
    arquivo_path: Annotated[str, StringConstraints(max_length=500)]


class DocumentoRead(TimestampedORM):
    conta_id: UUID
    estabelecimento_id: UUID | None
    tipo_documento_id: UUID
    numero: str | None
    data_emissao: date | None
    data_vencimento: date | None
    arquivo_path: str
    mime: str
    tamanho_bytes: int
    status: DocumentoStatus
    substitui_id: UUID | None
    motivo_rejeicao: str | None


class DocumentoRejeitar(BaseModel):
    motivo: Annotated[str, StringConstraints(min_length=3, max_length=500)]
