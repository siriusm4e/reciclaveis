"""Helper para gravar AuditLog (INSERT only)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def gravar_auditoria(
    db: AsyncSession,
    *,
    acao: str,
    recurso_tipo: str,
    recurso_id: UUID | None = None,
    conta_afetada_id: UUID | None = None,
    payload: dict[str, Any] | None = None,
    motivo: str | None = None,
    admin_id: UUID | None = None,
    usuario_id: UUID | None = None,
    request: Request | None = None,
) -> AuditLog:
    log = AuditLog(
        acao=acao,
        recurso_tipo=recurso_tipo,
        recurso_id=recurso_id,
        conta_afetada_id=conta_afetada_id,
        payload=payload or {},
        motivo=motivo,
        admin_id=admin_id,
        usuario_id=usuario_id,
        ip=(request.client.host if request and request.client else None),
        user_agent=(request.headers.get("user-agent") if request else None),
    )
    db.add(log)
    await db.flush()
    return log
