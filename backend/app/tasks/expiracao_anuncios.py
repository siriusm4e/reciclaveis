"""Daily — expira anúncios (venda, oferta, máquina, serviço, frete) com prazo vencido + desativa boost."""

from __future__ import annotations

import structlog

from app.db.session import SessionLocal
from app.models.anuncio_frete import AnuncioFrete
from app.models.anuncio_maquina import AnuncioMaquina
from app.models.anuncio_servico import AnuncioServico
from app.repositories.marketplace import (
    AnuncioVendaRepository,
    OfertaCompraRepository,
)
from app.repositories.outros_anuncios import expirar_anuncios_status_generico
from app.tasks._helpers import run_async
from app.tasks.celery_app import celery_app

log = structlog.get_logger(__name__)


async def _run() -> dict:
    async with SessionLocal() as db:
        out = {
            "anuncios_venda": await AnuncioVendaRepository(db).expirar_vencidos(),
            "ofertas_compra": await OfertaCompraRepository(db).expirar_vencidos(),
            "boost_desativados": await OfertaCompraRepository(db).desativar_boost_expirado(),
            "maquinas": await expirar_anuncios_status_generico(db, AnuncioMaquina),
            "servicos": await expirar_anuncios_status_generico(db, AnuncioServico),
            "fretes": await expirar_anuncios_status_generico(db, AnuncioFrete),
        }
        await db.commit()
        return out


@celery_app.task(name="task_expirar_anuncios")
def task_expirar_anuncios() -> dict:
    res = run_async(_run())
    log.info("task_expirar_anuncios", **res)
    return res
