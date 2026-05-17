"""Daily — Negociações COMBINADA há 7+ dias → CONCLUIDA (automático)."""

from __future__ import annotations

import structlog

from app.db.session import SessionLocal
from app.repositories.negociacao import NegociacaoRepository
from app.tasks._helpers import run_async
from app.tasks.celery_app import celery_app

log = structlog.get_logger(__name__)


@celery_app.task(name="task_concluir_negociacoes_combinadas")
def task_concluir_negociacoes_combinadas() -> int:
    async def _run() -> int:
        async with SessionLocal() as db:
            n = await NegociacaoRepository(db).concluir_combinadas_antigas(dias=7)
            await db.commit()
            return n

    n = run_async(_run())
    log.info("task_concluir_negociacoes_combinadas", concluidas=n)
    return n
