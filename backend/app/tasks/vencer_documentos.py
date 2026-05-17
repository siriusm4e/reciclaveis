"""Daily 00:00 UTC — move Documentos cuja data_vencimento < hoje para VENCIDO."""

from __future__ import annotations

from datetime import date

import structlog

from app.db.session import SessionLocal
from app.repositories.documento import DocumentoRepository
from app.tasks._helpers import run_async
from app.tasks.celery_app import celery_app

log = structlog.get_logger(__name__)


async def _run() -> int:
    async with SessionLocal() as db:
        n = await DocumentoRepository(db).vencer_documentos(hoje=date.today())
        await db.commit()
        return n


@celery_app.task(name="task_vencer_documentos")
def task_vencer_documentos() -> int:
    n = run_async(_run())
    log.info("task_vencer_documentos", vencidos=n)
    return n
