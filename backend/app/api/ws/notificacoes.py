"""WebSocket — notificações em tempo real por Conta (pub/sub Redis).

Conexão: ws://host/ws/notificacoes?token=<access_token>&conta_id=<uuid>

Receberá eventos publicados em `notificacoes:conta:{conta_id}` por outros services
(ex.: alerta pago disparado, documento aprovado, negociação aceita).
"""

from __future__ import annotations

import asyncio
import json
from uuid import UUID

import structlog
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select

from app.core.redis_client import is_jti_blocked
from app.core.security import TOKEN_TYPE_ACCESS, decode_token
from app.db.session import SessionLocal
from app.models.membro import Membro
from app.utils.ws_pubsub import assinar, canal_notificacoes_conta

log = structlog.get_logger(__name__)
router = APIRouter()


@router.websocket("/ws/notificacoes")
async def notificacoes(
    websocket: WebSocket,
    token: str = Query(...),
    conta_id: UUID = Query(...),
):
    try:
        payload = decode_token(token, expected_type=TOKEN_TYPE_ACCESS)
        if await is_jti_blocked(payload["jti"]):
            raise RuntimeError("jti revogado")
        usuario_id = UUID(payload["sub"])
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    async with SessionLocal() as db:
        membro = await db.scalar(
            select(Membro).where(Membro.usuario_id == usuario_id, Membro.conta_id == conta_id)
        )
        if membro is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await websocket.accept()
    canal = canal_notificacoes_conta(conta_id)
    log.info("ws_notif_conectado", conta_id=str(conta_id), usuario_id=str(usuario_id))

    async def _forward() -> None:
        async for evento in assinar(canal):
            try:
                await websocket.send_text(json.dumps(evento, default=str))
            except Exception:
                return

    forward_task = asyncio.create_task(_forward())

    try:
        while True:
            # Apenas mantém vivo; cliente pode enviar ping
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        log.info("ws_notif_desconectado", conta_id=str(conta_id))
    finally:
        forward_task.cancel()
        try:
            await forward_task
        except Exception:
            pass
