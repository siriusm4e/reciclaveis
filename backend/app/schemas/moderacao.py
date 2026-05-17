"""Schemas — Denuncia, DecisaoModeracao, PerfilInterno, AuditLog."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

from app.models.enums import (
    AcaoModeracao,
    DenunciaAlvoTipo,
    DenunciaStatus,
    DenunciaTipoFechado,
    PerfilInternoTipo,
)
from app.schemas.common import ORMModel, TimestampedORM


# === Denúncia ===

class DenunciaCreate(BaseModel):
    alvo_tipo: DenunciaAlvoTipo
    alvo_id: UUID
    tipo_fechado: DenunciaTipoFechado
    descricao: Annotated[str, StringConstraints(min_length=10, max_length=2000)]


class DenunciaRead(TimestampedORM):
    denunciante_conta_id: UUID
    alvo_tipo: DenunciaAlvoTipo
    alvo_id: UUID
    tipo_fechado: DenunciaTipoFechado
    descricao: str
    status: DenunciaStatus


# === DecisaoModeracao ===

class DecisaoModeracaoCreate(BaseModel):
    acao: AcaoModeracao
    motivo: Annotated[str, StringConstraints(min_length=3, max_length=2000)]


class DecisaoModeracaoRead(TimestampedORM):
    denuncia_id: UUID
    admin_id: UUID
    acao: AcaoModeracao
    motivo: str


# === PerfilInterno (M16) ===

class PerfilInternoCreate(BaseModel):
    usuario_id: UUID
    tipo: PerfilInternoTipo


class PerfilInternoRead(TimestampedORM):
    usuario_id: UUID
    tipo: PerfilInternoTipo
    ativo: bool


# === AuditLog ===

class AuditLogRead(ORMModel):
    id: UUID
    admin_id: UUID | None
    usuario_id: UUID | None
    acao: str
    recurso_tipo: str
    recurso_id: UUID | None
    conta_afetada_id: UUID | None
    payload: dict
    motivo: str | None
    ip: str | None
    user_agent: str | None
    created_at: datetime


# === Config admin (limiar de cobertura, prazo oportunidade pública) ===

class LimiarCoberturaUpdate(BaseModel):
    valor: int = Field(ge=1, le=50)


class PrazoOportunidadePublicaUpdate(BaseModel):
    dias_uteis: int = Field(ge=1, le=30)
