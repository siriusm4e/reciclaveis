"""Rotas de autenticação — register, login, MFA, refresh, logout, convites."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    ValidationDomainError,
)
from app.core.redis_client import blocklist_jti, is_jti_blocked
from app.core.security import (
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_mfa_secret,
    generate_opaque_token,
    hash_password,
    mfa_provisioning_uri,
    needs_password_rehash,
    verify_mfa_code,
    verify_password,
)
from app.db.session import get_db
from app.models.convite import ConviteMembro
from app.models.enums import ConviteStatus
from app.models.membro import Membro
from app.models.usuario import Usuario
from app.schemas.auth import (
    LoginRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UsuarioPublic,
)
from app.schemas.common import OkResponse
from app.schemas.identidade import ConviteAceitar, ConviteRead

router = APIRouter(prefix="/api/auth", tags=["auth"])


# === Helpers ===

def _token_pair(usuario: Usuario) -> TokenPair:
    access, _, exp = create_access_token(str(usuario.id))
    refresh, _, _ = create_refresh_token(str(usuario.id))
    return TokenPair(
        access_token=access,
        refresh_token=refresh,
        expires_in=int((exp - datetime.now(tz=timezone.utc)).total_seconds()),
    )


# === Register / confirm e-mail ===

@router.post("/register", response_model=UsuarioPublic, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Usuario:
    existing = await db.scalar(
        select(Usuario).where((Usuario.email == payload.email) | (Usuario.cpf == payload.cpf))
    )
    if existing is not None:
        raise ConflictError("E-mail ou CPF já cadastrado")

    user = Usuario(
        cpf=payload.cpf,
        email=str(payload.email),
        senha_hash=hash_password(payload.senha),
        nome_completo=payload.nome_completo,
        telefone=payload.telefone,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    # TODO: enviar e-mail de confirmação (serviço externo — fora do escopo do MVP)
    return user


# === Login + MFA ===

@router.post("/login", response_model=TokenPair)
async def login(
    payload: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenPair:
    user = await db.scalar(select(Usuario).where(Usuario.email == str(payload.email)))
    if user is None or not user.ativo:
        raise UnauthorizedError("Credenciais inválidas")

    now = datetime.now(tz=timezone.utc)
    if user.bloqueado_ate and user.bloqueado_ate > now:
        raise UnauthorizedError("Conta temporariamente bloqueada — tente novamente em alguns minutos")

    if not verify_password(payload.senha, user.senha_hash):
        user.login_falhos += 1
        if user.login_falhos >= settings.MFA_LOGIN_LOCK_THRESHOLD:
            user.bloqueado_ate = now + timedelta(minutes=15)
            user.login_falhos = 0
        await db.commit()
        raise UnauthorizedError("Credenciais inválidas")

    # Rehash transparente se hash legado (bcrypt → argon2)
    if needs_password_rehash(user.senha_hash):
        user.senha_hash = hash_password(payload.senha)

    if user.mfa_ativo:
        if not payload.mfa_code:
            raise UnauthorizedError("Código MFA obrigatório", details={"mfa_required": True})
        if not verify_mfa_code(user.mfa_secret or "", payload.mfa_code):
            user.login_falhos += 1
            await db.commit()
            raise UnauthorizedError("Código MFA inválido")

    user.login_falhos = 0
    user.bloqueado_ate = None
    await db.commit()
    return _token_pair(user)


# === Refresh + logout ===

@router.post("/refresh", response_model=TokenPair)
async def refresh(
    payload: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenPair:
    decoded = decode_token(payload.refresh_token, expected_type=TOKEN_TYPE_REFRESH)
    jti = decoded["jti"]
    # Token já rotacionado / revogado → recusa
    if await is_jti_blocked(jti):
        raise UnauthorizedError("Refresh token já utilizado ou revogado")
    # Rotaciona: bloqueia o jti antigo para evitar reuso.
    exp = int(decoded["exp"])
    ttl = max(1, exp - int(datetime.now(tz=timezone.utc).timestamp()))
    await blocklist_jti(jti, ttl_seconds=ttl)

    user = await db.scalar(select(Usuario).where(Usuario.id == UUID(decoded["sub"])))
    if user is None or not user.ativo:
        raise UnauthorizedError("Usuário não encontrado ou desativado")
    return _token_pair(user)


@router.post("/logout", response_model=OkResponse)
async def logout(payload: RefreshRequest) -> OkResponse:
    """Revoga o refresh token recebido (best-effort para o access)."""
    try:
        decoded = decode_token(payload.refresh_token, expected_type=TOKEN_TYPE_REFRESH)
    except UnauthorizedError:
        return OkResponse(ok=True)
    jti = decoded["jti"]
    exp = int(decoded["exp"])
    ttl = max(1, exp - int(datetime.now(tz=timezone.utc).timestamp()))
    await blocklist_jti(jti, ttl_seconds=ttl)
    return OkResponse(ok=True)


# === MFA setup / verify ===

@router.post("/mfa/setup", response_model=MFASetupResponse)
async def mfa_setup(
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MFASetupResponse:
    if current_user.mfa_ativo:
        raise ConflictError("MFA já está ativo")
    secret = generate_mfa_secret()
    current_user.mfa_secret = secret
    await db.commit()
    return MFASetupResponse(
        secret=secret,
        otpauth_uri=mfa_provisioning_uri(secret, account_name=current_user.email),
    )


@router.post("/mfa/verify", response_model=OkResponse)
async def mfa_verify(
    payload: MFAVerifyRequest,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OkResponse:
    if not current_user.mfa_secret:
        raise ValidationDomainError("MFA não configurado")
    if not verify_mfa_code(current_user.mfa_secret, payload.code):
        raise UnauthorizedError("Código inválido")
    current_user.mfa_ativo = True
    await db.commit()
    return OkResponse(ok=True)


# === Convites de Membro ===

@router.get("/convites/{token}", response_model=ConviteRead)
async def get_convite(
    token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ConviteMembro:
    convite = await db.scalar(select(ConviteMembro).where(ConviteMembro.token == token))
    if convite is None:
        raise NotFoundError("Convite não encontrado")
    now = datetime.now(tz=timezone.utc)
    if convite.status == ConviteStatus.PENDENTE and convite.expira_em < now:
        convite.status = ConviteStatus.EXPIRADO
        await db.commit()
    return convite


@router.post("/convites/{token}/aceitar", response_model=OkResponse)
async def aceitar_convite(
    token: str,
    _payload: ConviteAceitar,  # validação de schema (token também no body)
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OkResponse:
    convite = await db.scalar(select(ConviteMembro).where(ConviteMembro.token == token))
    if convite is None:
        raise NotFoundError("Convite não encontrado")
    if convite.status != ConviteStatus.PENDENTE:
        raise ConflictError(f"Convite no estado {convite.status.value}")
    if convite.expira_em < datetime.now(tz=timezone.utc):
        convite.status = ConviteStatus.EXPIRADO
        await db.commit()
        raise ConflictError("Convite expirado")

    if convite.email.lower() != current_user.email.lower():
        raise UnauthorizedError("Convite emitido para outro e-mail")

    # Cria Membro
    existing = await db.scalar(
        select(Membro).where(
            Membro.usuario_id == current_user.id, Membro.conta_id == convite.conta_id
        )
    )
    if existing is None:
        db.add(
            Membro(
                usuario_id=current_user.id,
                conta_id=convite.conta_id,
                papel_interno=convite.papel_interno,
            )
        )

    convite.status = ConviteStatus.ACEITO
    convite.aceito_por_usuario_id = current_user.id
    await db.commit()
    return OkResponse(ok=True)


# === Util — opaque token para confirmação de e-mail (usado em serviços) ===

def _new_email_confirmation_token() -> str:
    """Exposto aqui para conveniência; uso real no service de cadastro."""
    return generate_opaque_token()


@router.get("/me", response_model=UsuarioPublic)
async def me(current_user: Annotated[Usuario, Depends(get_current_user)]) -> Usuario:
    return current_user


# Marca request como autenticado — útil para correlacionar logs
async def _bind_user_to_log(request: Request, user_id: UUID) -> None:
    import structlog

    structlog.contextvars.bind_contextvars(usuario_id=str(user_id))
