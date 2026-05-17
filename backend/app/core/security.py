"""Senha (Argon2id + bcrypt legado), JWT (access/refresh + rotation) e MFA TOTP.

Decisões:
- CryptContext com Argon2id como default; bcrypt mantido para hashes legados.
  `pwd_context.needs_update(hash)` permite rehash transparente no próximo login.
- JWT com `jti` único; refresh tokens são *opaquely* rastreados pelo seu jti via
  Redis (blocklist na revogação + denylist após rotação). Access tokens curtos
  (15min) podem ficar válidos até expirar; para revogação imediata, blocklist por jti.
- MFA TOTP via pyotp; segredo persistido criptografado opcionalmente (não no MVP).
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
import pyotp
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import UnauthorizedError

# =============================================================================
# Senhas
# =============================================================================

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated=["bcrypt"],
    argon2__memory_cost=settings.ARGON2_MEMORY_COST,
    argon2__time_cost=settings.ARGON2_TIME_COST,
    argon2__parallelism=settings.ARGON2_PARALLELISM,
)


def hash_password(plain: str) -> str:
    """Gera hash Argon2id."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica senha (aceita Argon2id ou bcrypt legado)."""
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def needs_password_rehash(hashed: str) -> bool:
    """True se hash está em esquema deprecated (bcrypt) — rehash transparente no próximo login."""
    return pwd_context.needs_update(hashed)


# =============================================================================
# JWT
# =============================================================================

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)


def _build_token(
    *,
    subject: str,
    token_type: str,
    ttl: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, str, datetime]:
    """Retorna (token_encoded, jti, expires_at_utc)."""
    issued_at = _now_utc()
    expires_at = issued_at + ttl
    jti = uuid4().hex
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
        "iss": settings.JWT_ISSUER,
        "jti": jti,
    }
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti, expires_at


def create_access_token(
    subject: str,
    *,
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, str, datetime]:
    return _build_token(
        subject=subject,
        token_type=TOKEN_TYPE_ACCESS,
        ttl=timedelta(minutes=settings.JWT_ACCESS_TOKEN_TTL_MINUTES),
        extra_claims=extra_claims,
    )


def create_refresh_token(
    subject: str,
    *,
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, str, datetime]:
    return _build_token(
        subject=subject,
        token_type=TOKEN_TYPE_REFRESH,
        ttl=timedelta(days=settings.JWT_REFRESH_TOKEN_TTL_DAYS),
        extra_claims=extra_claims,
    )


def decode_token(token: str, *, expected_type: str | None = None) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "iat", "sub", "type", "jti"]},
            issuer=settings.JWT_ISSUER,
        )
    except jwt.ExpiredSignatureError as e:
        raise UnauthorizedError("Token expirado") from e
    except jwt.InvalidTokenError as e:
        raise UnauthorizedError("Token inválido") from e
    if expected_type and payload.get("type") != expected_type:
        raise UnauthorizedError(f"Token de tipo inesperado: {payload.get('type')}")
    return payload


# =============================================================================
# MFA TOTP
# =============================================================================

def generate_mfa_secret() -> str:
    """Base32 secret para TOTP."""
    return pyotp.random_base32()


def mfa_provisioning_uri(secret: str, *, account_name: str) -> str:
    """URI para QR code (otpauth://...)."""
    return pyotp.TOTP(secret).provisioning_uri(name=account_name, issuer_name=settings.MFA_ISSUER)


def verify_mfa_code(secret: str, code: str) -> bool:
    """Valida TOTP com tolerância de ±1 step (30s) para drift de relógio."""
    if not secret or not code:
        return False
    return pyotp.TOTP(secret).verify(code, valid_window=1)


# =============================================================================
# Tokens opacos (convites de Membro, confirmação de e-mail)
# =============================================================================

def generate_opaque_token(*, byte_length: int = 32) -> str:
    """Token URL-safe para convites/confirmação de e-mail."""
    return secrets.token_urlsafe(byte_length)
