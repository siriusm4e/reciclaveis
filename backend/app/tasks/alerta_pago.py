"""Imediato — disparo de Alerta Pago para uma OfertaCompra com auditoria de cobertura/reembolso."""

from __future__ import annotations

from uuid import UUID

import structlog

from app.db.session import SessionLocal
from app.services.alerta_pago_service import AlertaPagoService
from app.tasks._helpers import run_async
from app.tasks.celery_app import celery_app

log = structlog.get_logger(__name__)


@celery_app.task(name="task_processar_alerta_pago", bind=True, max_retries=2)
def task_processar_alerta_pago(
    self, oferta_id: str, raio_km: int, duracao_horas: int, segmentacao: dict
) -> dict:
    async def _run() -> dict:
        async with SessionLocal() as db:
            svc = AlertaPagoService(db)
            res = await svc.ativar(
                oferta_id=UUID(oferta_id),
                raio_km=raio_km,
                duracao_horas=duracao_horas,
                segmentacao=segmentacao,
            )
            await db.commit()
            return res

    try:
        res = run_async(_run())
        log.info("task_processar_alerta_pago", oferta_id=oferta_id, **{k: v for k, v in res.items() if k != "oferta_id"})
        return {**res, "oferta_id": oferta_id}
    except Exception as e:  # noqa: BLE001
        log.warning("alerta_pago_falhou", oferta_id=oferta_id, error=str(e))
        raise self.retry(exc=e, countdown=10)
