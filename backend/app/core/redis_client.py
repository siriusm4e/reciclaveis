"""Cliente Redis centralizado — cache, pub/sub, blocklist JWT."""

from __future__ import annotations

from functools import lru_cache

import redis.asyncio as redis

from app.core.config import settings


@lru_cache(maxsize=1)
def get_redis_cache() -> redis.Redis:
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


@lru_cache(maxsize=1)
def get_redis_blocklist() -> redis.Redis:
    """DB separado para blocklist de JWT (TTL próprio)."""
    return redis.from_url(settings.JWT_BLOCKLIST_REDIS_URL, decode_responses=True)


@lru_cache(maxsize=1)
def get_redis_pubsub() -> redis.Redis:
    """DB separado para pub/sub WebSocket multi-instância."""
    return redis.from_url(settings.WS_PUBSUB_REDIS_URL, decode_responses=False)


# === JWT blocklist helpers ===

def _blocklist_key(jti: str) -> str:
    return f"jwt:blocklist:{jti}"


async def blocklist_jti(jti: str, *, ttl_seconds: int) -> None:
    """Marca jti como revogado por `ttl_seconds` (>= TTL restante do token)."""
    r = get_redis_blocklist()
    await r.setex(_blocklist_key(jti), ttl_seconds, "1")


async def is_jti_blocked(jti: str) -> bool:
    r = get_redis_blocklist()
    return bool(await r.exists(_blocklist_key(jti)))


# === Banimento de Conta (acesso revogado ≤ 5min via blocklist) ===

def _conta_ban_key(conta_id: str) -> str:
    return f"conta:banned:{conta_id}"


async def ban_conta(conta_id: str, *, ttl_seconds: int = 60 * 60 * 24 * 365) -> None:
    r = get_redis_blocklist()
    await r.setex(_conta_ban_key(conta_id), ttl_seconds, "1")


async def is_conta_banned(conta_id: str) -> bool:
    r = get_redis_blocklist()
    return bool(await r.exists(_conta_ban_key(conta_id)))
