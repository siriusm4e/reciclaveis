"""Daily — ciclo de Assinatura (renovação, graça → pausada, pausada → cancelada)."""

from __future__ import annotations

import structlog

from app.db.session import SessionLocal
from app.repositories.assinatura import AssinaturaRepository
from app.services.assinatura_service import AssinaturaService
from app.tasks._helpers import run_async
from app.tasks.celery_app import celery_app

log = structlog.get_logger(__name__)


@celery_app.task(name="task_renovar_assinaturas")
def task_renovar_assinaturas() -> int:
    async def _run() -> int:
        async with SessionLocal() as db:
            svc = AssinaturaService(db)
            repo = AssinaturaRepository(db)
            assinaturas = await repo.listar_para_renovar()
            renovadas = 0
            for a in assinaturas:
                await svc.gerar_renovacao(a)
                renovadas += 1
            await db.commit()
            return renovadas

    n = run_async(_run())
    log.info("task_renovar_assinaturas", renovadas=n)
    return n


@celery_app.task(name="task_processar_graca")
def task_processar_graca() -> int:
    async def _run() -> int:
        async with SessionLocal() as db:
            n = await AssinaturaRepository(db).vencer_em_graca(dias_graca=7)
            await db.commit()
            return n

    n = run_async(_run())
    log.info("task_processar_graca", pausadas=n)
    return n


@celery_app.task(name="task_processar_pausada")
def task_processar_pausada() -> int:
    async def _run() -> int:
        async with SessionLocal() as db:
            n = await AssinaturaRepository(db).cancelar_pausadas_antigas(dias_pausada=60)
            await db.commit()
            return n

    n = run_async(_run())
    log.info("task_processar_pausada", canceladas=n)
    return n
