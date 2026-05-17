"""Celery app — broker/backend Redis + beat schedule completo."""

from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings


celery_app = Celery(
    "pnr",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.expiracao_convites",
        "app.tasks.alertas_vencimento",
        "app.tasks.vencer_documentos",
        "app.tasks.expiracao_anuncios",
        "app.tasks.expiracao_negociacoes",
        "app.tasks.conclusao_negociacoes",
        "app.tasks.janela_avaliacao",
        "app.tasks.alerta_pago",
        "app.tasks.assinaturas",
        "app.tasks.retentativa_pagamento",
        "app.tasks.anonimizacao_lgpd",
        "app.tasks.encerrar_oportunidades",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.TZ,
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)

celery_app.conf.beat_schedule = {
    # === Identidade ===
    "expirar-convites-hourly": {
        "task": "task_expirar_convites",
        "schedule": crontab(minute=0),
    },
    # === Documentos ===
    "alertas-vencimento-08utc": {
        "task": "task_alertas_vencimento_documentos",
        "schedule": crontab(hour=8, minute=0),
    },
    "vencer-documentos-00utc": {
        "task": "task_vencer_documentos",
        "schedule": crontab(hour=0, minute=5),
    },
    # === Anúncios / boost ===
    "expirar-anuncios-diario": {
        "task": "task_expirar_anuncios",
        "schedule": crontab(hour=0, minute=10),
    },
    # === Negociação ===
    "expirar-negociacoes-inativas-diario": {
        "task": "task_expirar_negociacoes_inativas",
        "schedule": crontab(hour=1, minute=0),
    },
    "expirar-combinado-unilateral-hourly": {
        "task": "task_expirar_combinado_unilateral",
        "schedule": crontab(minute=15),
    },
    "concluir-negociacoes-combinadas-diario": {
        "task": "task_concluir_negociacoes_combinadas",
        "schedule": crontab(hour=1, minute=30),
    },
    # === Reputação ===
    "revelar-avaliacoes-diario": {
        "task": "task_revelar_avaliacoes",
        "schedule": crontab(hour=2, minute=0),
    },
    # === Assinaturas ===
    "renovar-assinaturas-diario": {
        "task": "task_renovar_assinaturas",
        "schedule": crontab(hour=3, minute=0),
    },
    "graca-vencer-diario": {
        "task": "task_processar_graca",
        "schedule": crontab(hour=3, minute=15),
    },
    "pausada-cancelar-diario": {
        "task": "task_processar_pausada",
        "schedule": crontab(hour=3, minute=30),
    },
    "retentativa-pagamento-hourly": {
        "task": "task_retentativa_pagamento",
        "schedule": crontab(minute=30),
    },
    # === LGPD ===
    "anonimizacao-lgpd-diario": {
        "task": "task_processar_exclusao_lgpd",
        "schedule": crontab(hour=4, minute=0),
    },
    # === Oportunidades ===
    "encerrar-oportunidades-hourly": {
        "task": "task_encerrar_oportunidades",
        "schedule": crontab(minute=45),
    },
}
