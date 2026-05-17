"""Pub/Sub Redis para WebSocket multi-instância (chat + notificações)."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator
from uuid import UUID

from app.core.redis_client import get_redis_pubsub


def canal_negociacao(negociacao_id: UUID | str) -> str:
    return f"negociacao:{negociacao_id}:mensagens"


def canal_notificacoes_conta(conta_id: UUID | str) -> str:
    return f"notificacoes:conta:{conta_id}"


async def publicar(canal: str, evento: str, payload: dict[str, Any]) -> int:
    redis = get_redis_pubsub()
    body = json.dumps({"evento": evento, "payload": payload}, default=str).encode("utf-8")
    return await redis.publish(canal, body)


async def assinar(canal: str) -> AsyncIterator[dict[str, Any]]:
    """Itera eventos do canal. Cancela ao sair do contexto."""
    redis = get_redis_pubsub()
    pubsub = redis.pubsub()
    await pubsub.subscribe(canal)
    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            data = message["data"]
            if isinstance(data, (bytes, bytearray)):
                data = data.decode("utf-8")
            try:
                yield json.loads(data)
            except json.JSONDecodeError:
                continue
    finally:
        await pubsub.unsubscribe(canal)
        await pubsub.aclose()
