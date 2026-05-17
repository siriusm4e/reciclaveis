"""Daily — Avaliações com 14+ dias sem reciprocidade → visíveis."""

from __future__ import annotations

import structlog

from app.db.session import SessionLocal
from app.repositories.negociacao import AvaliacaoRepository
from app.tasks._helpers import run_async
from app.tasks.celery_app import celery_app

log = structlog.get_logger(__name__)


@celery_app.task(name="task_revelar_avaliacoes")
def task_revelar_avaliacoes() -> int:
    async def _run() -> int:
        async with SessionLocal() as db:
            n = await AvaliacaoRepository(db).revelar_apos_janela(dias=14)
            await db.commit()
            return n

    n = run_async(_run())
    log.info("task_revelar_avaliacoes", reveladas=n)
    return n
