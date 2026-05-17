"""Daily 08:00 UTC — alertas D-30/D-15/D-7 de vencimento de Documento."""

from __future__ import annotations

import structlog

from app.db.session import SessionLocal
from app.repositories.conteudo import DispositivoRepository
from app.repositories.documento import DocumentoRepository
from app.tasks._helpers import run_async
from app.tasks.celery_app import celery_app
from app.utils.notifications import enviar_push

log = structlog.get_logger(__name__)


async def _run() -> dict:
    out = {"D-30": 0, "D-15": 0, "D-7": 0, "push_sucessos": 0, "push_falhas": 0}
    async with SessionLocal() as db:
        docs_repo = DocumentoRepository(db)
        disp_repo = DispositivoRepository(db)
        for dias in (30, 15, 7):
            docs = await docs_repo.listar_vencendo_em(dias=dias)
            out[f"D-{dias}"] = len(docs)
            for doc in docs:
                tokens = await disp_repo.tokens_ativos_de_conta(doc.conta_id)
                if not tokens:
                    continue
                resultado = enviar_push(
                    tokens=tokens,
                    titulo=f"Documento vence em {dias} dias",
                    corpo=f"Renove para manter operação ativa",
                    data={"documento_id": str(doc.id), "tipo": "vencimento_documento"},
                )
                out["push_sucessos"] += resultado["enviados"]
                out["push_falhas"] += resultado["falhas"]
        await db.commit()
    return out


@celery_app.task(name="task_alertas_vencimento_documentos")
def task_alertas_vencimento_documentos() -> dict:
    result = run_async(_run())
    log.info("task_alertas_vencimento_documentos", **result)
    return result
