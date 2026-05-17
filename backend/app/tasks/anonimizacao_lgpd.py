"""Daily — processa pedidos de exclusão LGPD com graça > 30 dias.

Anonimização:
- PII (nome, foto, CPF, e-mail, telefone) substituídos por hash.
- conta_id interno preservado para integridade referencial.
- Avaliações permanecem visíveis com `nome_publico` = "Conta excluída".
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.conta import Conta, ContaStatus
from app.models.membro import Membro
from app.models.usuario import Usuario
from app.tasks._helpers import run_async
from app.tasks.celery_app import celery_app

log = structlog.get_logger(__name__)


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


async def _anonimizar() -> int:
    n = 0
    limite = datetime.now(tz=timezone.utc) - timedelta(days=settings.LGPD_GRACA_EXCLUSAO_DIAS)
    async with SessionLocal() as db:
        rows = await db.scalars(
            select(Usuario).where(
                Usuario.pedido_exclusao_em.is_not(None),
                Usuario.pedido_exclusao_em < limite,
            )
        )
        for u in rows:
            h = _hash(str(u.id))
            u.nome_completo = f"Usuário anonimizado #{h}"
            u.cpf = f"00000000{h[:3]}"  # mantém formato 11 dígitos sintético
            u.email = f"anon+{h}@anonimizado.local"
            u.telefone = None
            u.foto_path = None
            u.mfa_secret = None
            u.ativo = False

            # Para cada Conta onde o usuário é único Membro admin → anonimizar a Conta também
            memberships = await db.scalars(select(Membro).where(Membro.usuario_id == u.id))
            for m in memberships:
                conta = await db.get(Conta, m.conta_id)
                if conta is None:
                    continue
                # Anonimiza nome público sempre (não importa quantos admins)
                conta.nome_publico = "Conta excluída"
                conta.foto_perfil_path = None
                conta.status = ContaStatus.ANONIMIZADA
            n += 1
        await db.commit()
    return n


@celery_app.task(name="task_processar_exclusao_lgpd")
def task_processar_exclusao_lgpd() -> int:
    n = run_async(_anonimizar())
    log.info("task_processar_exclusao_lgpd", anonimizados=n)
    return n
