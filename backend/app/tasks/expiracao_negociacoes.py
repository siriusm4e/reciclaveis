"""Daily — Negociações abertas sem mensagem por 14 dias → EXPIRADA.

Hourly — Sinalização unilateral 'combinado' sem confirmação em 48h → reset.
"""

from __future__ import annotations

import structlog

from app.db.session import SessionLocal
from app.repositories.negociacao import NegociacaoRepository
from app.tasks._helpers import run_async
from app.tasks.celery_app import celery_app

log = structlog.get_logger(__name__)


@celery_app.task(name="task_expirar_negociacoes_inativas")
def task_expirar_negociacoes_inativas() -> int:
    async def _run() -> int:
        async with SessionLocal() as db:
            n = await NegociacaoRepository(db).expirar_inativas(dias=14)
            await db.commit()
            return n

    n = run_async(_run())
    log.info("task_expirar_negociacoes_inativas", expiradas=n)
    return n


@celery_app.task(name="task_expirar_combinado_unilateral")
def task_expirar_combinado_unilateral() -> int:
    async def _run() -> int:
        async with SessionLocal() as db:
            n = await NegociacaoRepository(db).desfazer_sinalizacao_unilateral_expirada(horas=48)
            await db.commit()
            return n

    n = run_async(_run())
    log.info("task_expirar_combinado_unilateral", reset=n)
    return n
