"""Schemas de autenticação."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, StringConstraints

from app.schemas.common import ORMModel


Cpf = Annotated[str, StringConstraints(pattern=r"^\d{11}$")]
Password = Annotated[str, StringConstraints(min_length=6, max_length=128)]


class RegisterRequest(BaseModel):
    cpf: Cpf
    email: EmailStr
    senha: Password
    nome_completo: Annotated[str, StringConstraints(min_length=3, max_length=255)]
    telefone: Annotated[str, StringConstraints(pattern=r"^\d{10,11}$")] | None = None


class EmailConfirmRequest(BaseModel):
    token: Annotated[str, StringConstraints(min_length=20, max_length=128)]


class LoginRequest(BaseModel):
    email: EmailStr
    senha: Password
    mfa_code: Annotated[str, StringConstraints(pattern=r"^\d{6}$")] | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(description="Segundos até expiração do access token")


class RefreshRequest(BaseModel):
    refresh_token: str


class AlterarEmailRequest(BaseModel):
    senha_atual: str
    novo_email: EmailStr


class AlterarSenhaRequest(BaseModel):
    senha_atual: str
    nova_senha: Password


class MFASetupResponse(BaseModel):
    secret: str
    otpauth_uri: str


class MFAVerifyRequest(BaseModel):
    code: Annotated[str, StringConstraints(pattern=r"^\d{6}$")]


class PerfilInternoPublic(ORMModel):
    tipo: str
    ativo: bool


class UsuarioPublic(ORMModel):
    id: UUID
    email: EmailStr
    nome_completo: str
    telefone: str | None
    foto_path: str | None
    mfa_ativo: bool
    email_confirmado: bool
    ativo: bool
    created_at: datetime
    perfil_interno: PerfilInternoPublic | None = None
