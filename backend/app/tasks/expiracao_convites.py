"""Hourly — expira ConviteMembro pendente com expira_em < now."""

from __future__ import annotations

import structlog

from app.db.session import SessionLocal
from app.repositories.conta import ConviteRepository
from app.tasks._helpers import run_async
from app.tasks.celery_app import celery_app

log = structlog.get_logger(__name__)


async def _run() -> int:
    async with SessionLocal() as db:
        count = await ConviteRepository(db).expirar_vencidos()
        await db.commit()
        return count


@celery_app.task(name="task_expirar_convites")
def task_expirar_convites() -> int:
    n = run_async(_run())
    log.info("task_expirar_convites", expirados=n)
    return n
