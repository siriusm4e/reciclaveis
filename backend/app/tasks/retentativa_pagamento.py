"""Hourly — retenta Pagamentos falhos (até 3 vezes em 24h/48h/72h)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import structlog
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.enums import FaturaStatus, PagamentoMetodo, PagamentoStatus
from app.models.fatura import Fatura
from app.models.pagamento import Pagamento
from app.services.assinatura_service import AssinaturaService
from app.tasks._helpers import run_async
from app.tasks.celery_app import celery_app

log = structlog.get_logger(__name__)


# Janelas: tentativa 1→2 = 24h, 2→3 = 48h, 3→4 = 72h
JANELAS_HORAS = {1: 24, 2: 48, 3: 72}


async def _retentar() -> int:
    retentados = 0
    async with SessionLocal() as db:
        svc = AssinaturaService(db)
        rows = await db.scalars(
            select(Fatura).where(Fatura.status == FaturaStatus.FALHA)
        )
        for fatura in rows:
            ultima = await db.scalar(
                select(Pagamento)
                .where(Pagamento.fatura_id == fatura.id)
                .order_by(Pagamento.tentativa.desc())
                .limit(1)
            )
            if ultima is None or ultima.tentativa >= 4:
                continue
            janela = JANELAS_HORAS.get(ultima.tentativa, 72)
            if ultima.created_at + timedelta(hours=janela) > datetime.now(tz=timezone.utc):
                continue
            await svc.registrar_pagamento(
                fatura=fatura,
                valor_centavos=fatura.valor_centavos,
                metodo=PagamentoMetodo.CARTAO,
                status=PagamentoStatus.PENDENTE,
                mensagem="Retentativa automática",
            )
            retentados += 1
        await db.commit()
    return retentados


@celery_app.task(name="task_retentativa_pagamento")
def task_retentativa_pagamento() -> int:
    n = run_async(_retentar())
    log.info("task_retentativa_pagamento", retentados=n)
    return n
