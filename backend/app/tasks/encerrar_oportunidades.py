"""Hourly — encerra Oportunidades cujo prazo_submissao já passou.

Após 72h da encerramento, propostas SUBMETIDAS viram EXPIRADAS.
"""

from __future__ import annotations

import structlog

from app.db.session import SessionLocal
from app.repositories.oportunidade import OportunidadeRepository, PropostaRepository
from app.tasks._helpers import run_async
from app.tasks.celery_app import celery_app

log = structlog.get_logger(__name__)


@celery_app.task(name="task_encerrar_oportunidades")
def task_encerrar_oportunidades() -> dict:
    async def _run() -> dict:
        async with SessionLocal() as db:
            encerradas = await OportunidadeRepository(db).encerrar_prazo_vencido()
            expiradas = await PropostaRepository(db).expirar_pendentes_apos_encerramento(horas=72)
            await db.commit()
            return {"oportunidades_encerradas": encerradas, "propostas_expiradas": expiradas}

    res = run_async(_run())
    log.info("task_encerrar_oportunidades", **res)
    return res
