"""WebSocket — chat por Negociação (pub/sub Redis).

Conexão: ws://host/ws/negociacao/{negociacao_id}?token=<access_token>&conta_id=<uuid>

Cliente recebe eventos JSON: {"evento": "nova_mensagem"|"status_alterado", "payload": {...}}.
Cliente pode enviar mensagens JSON: {"conteudo": "..."} → backend grava + publica.
"""

from __future__ import annotations

import json
from uuid import UUID

import structlog
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.core.exceptions import UnauthorizedError
from app.core.redis_client import is_jti_blocked
from app.core.security import TOKEN_TYPE_ACCESS, decode_token
from app.db.session import SessionLocal
from app.models.enums import MensagemTipo
from app.repositories.negociacao import NegociacaoRepository
from app.services.negociacao_service import NegociacaoService
from app.utils.ws_pubsub import assinar, canal_negociacao

log = structlog.get_logger(__name__)
router = APIRouter()


async def _autenticar(token: str) -> UUID:
    payload = decode_token(token, expected_type=TOKEN_TYPE_ACCESS)
    if await is_jti_blocked(payload["jti"]):
        raise UnauthorizedError("Sessão revogada")
    return UUID(payload["sub"])


@router.websocket("/ws/negociacao/{negociacao_id}")
async def chat_negociacao(
    websocket: WebSocket,
    negociacao_id: UUID,
    token: str = Query(...),
    conta_id: UUID = Query(..., description="Conta ativa do usuário"),
):
    # 1. Autenticação via query string (WebSocket não suporta header customizado em browsers)
    try:
        usuario_id = await _autenticar(token)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Verifica que a Conta participa da Negociação
    async with SessionLocal() as db:
        neg = await NegociacaoRepository(db).get(negociacao_id)
        if neg is None or conta_id not in (neg.conta_vendedora_id, neg.conta_compradora_id):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await websocket.accept()
    canal = canal_negociacao(negociacao_id)
    log.info("ws_chat_conectado", negociacao_id=str(negociacao_id), conta_id=str(conta_id))

    import asyncio

    async def _forward() -> None:
        async for evento in assinar(canal):
            try:
                await websocket.send_text(json.dumps(evento, default=str))
            except Exception:
                return

    forward_task = asyncio.create_task(_forward())

    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"erro": "json_invalido"}))
                continue

            conteudo = (payload.get("conteudo") or "").strip()
            if not conteudo:
                continue

            async with SessionLocal() as db:
                neg = await NegociacaoRepository(db).get(negociacao_id)
                if neg is None:
                    await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
                    return
                svc = NegociacaoService(db)
                try:
                    await svc.enviar_mensagem(
                        negociacao=neg,
                        conta_remetente_id=conta_id,
                        usuario_remetente_id=usuario_id,
                        conteudo=conteudo,
                        tipo=MensagemTipo.TEXTO,
                    )
                    await db.commit()
                except Exception as e:  # noqa: BLE001
                    await db.rollback()
                    await websocket.send_text(json.dumps({"erro": str(e)}))
    except WebSocketDisconnect:
        log.info("ws_chat_desconectado", negociacao_id=str(negociacao_id))
    finally:
        forward_task.cancel()
        try:
            await forward_task
        except Exception:
            pass
