"""Push notifications — FCM (Android) e APNs (iOS) via Firebase Admin SDK.

Em ambiente sem credenciais (dev local), o serviço entra em modo "dry-run":
imprime no log estruturado e retorna ack falso, sem falhar a requisição.
"""

from __future__ import annotations

import base64
import json
from functools import lru_cache
from typing import Sequence

import structlog

from app.core.config import settings

log = structlog.get_logger(__name__)


@lru_cache(maxsize=1)
def _firebase_app():
    """Inicializa Firebase Admin SDK uma vez. Retorna None em modo dry-run."""
    if not settings.FCM_CREDENTIALS_JSON_BASE64 or not settings.FCM_PROJECT_ID:
        log.info("fcm_dry_run", reason="missing_credentials")
        return None
    try:
        import firebase_admin
        from firebase_admin import credentials

        raw = base64.b64decode(settings.FCM_CREDENTIALS_JSON_BASE64)
        cred_dict = json.loads(raw)
        cred = credentials.Certificate(cred_dict)
        return firebase_admin.initialize_app(cred, options={"projectId": settings.FCM_PROJECT_ID})
    except Exception as e:  # noqa: BLE001
        log.warning("fcm_init_failed", error=str(e))
        return None


def enviar_push(
    *,
    tokens: Sequence[str],
    titulo: str,
    corpo: str,
    data: dict[str, str] | None = None,
) -> dict[str, int]:
    """Envia push a um conjunto de tokens. Retorna `{enviados, falhas}`.

    Em dry-run (sem credenciais), apenas loga e retorna `{enviados: 0, falhas: 0}`.
    """
    if not tokens:
        return {"enviados": 0, "falhas": 0}

    app = _firebase_app()
    if app is None:
        log.info("push_dry_run", count=len(tokens), titulo=titulo)
        return {"enviados": 0, "falhas": 0}

    from firebase_admin import messaging

    # FCM aceita até 500 tokens por multicast
    sucessos = 0
    falhas = 0
    notification = messaging.Notification(title=titulo, body=corpo)
    batch_size = 500
    for i in range(0, len(tokens), batch_size):
        batch = list(tokens[i : i + batch_size])
        msg = messaging.MulticastMessage(
            tokens=batch,
            notification=notification,
            data={k: str(v) for k, v in (data or {}).items()},
        )
        try:
            resp = messaging.send_each_for_multicast(msg)
            sucessos += resp.success_count
            falhas += resp.failure_count
        except Exception as e:  # noqa: BLE001
            log.warning("push_batch_failed", error=str(e), batch_size=len(batch))
            falhas += len(batch)

    log.info("push_enviado", titulo=titulo, sucessos=sucessos, falhas=falhas)
    return {"enviados": sucessos, "falhas": falhas}
