"""Backoffice — Contas (operador_atendimento, gestor_institucional)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_perfil_interno
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.conta import Conta, ContaTipo
from app.models.enums import ContaStatus
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.identidade import ContaRead, ContaStatusUpdate
from app.services.identidade_service import IdentidadeService
from app.utils.audit import gravar_auditoria

router = APIRouter(prefix="/api/admin/contas", tags=["admin:contas"])


@router.get(
    "/",
    response_model=list[ContaRead],
    dependencies=[Depends(require_perfil_interno("superadmin", "operador_atendimento", "gestor_institucional"))],
)
async def listar(
    db: Annotated[AsyncSession, Depends(get_db)],
    tipo: ContaTipo | None = Query(default=None),
    status_: ContaStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    repo = BaseRepository[Conta](db)
    repo.model = Conta  # type: ignore[assignment]
    where = []
    if tipo:
        where.append(Conta.tipo == tipo)
    if status_:
        where.append(Conta.status == status_)
    return await repo.list(limit=page_size, offset=(page - 1) * page_size, where=where)


@router.patch(
    "/{conta_id}/status",
    response_model=ContaRead,
    dependencies=[Depends(require_perfil_interno("superadmin", "operador_atendimento"))],
)
async def mudar_status(
    conta_id: UUID,
    payload: ContaStatusUpdate,
    request: Request,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    conta = await db.get(Conta, conta_id)
    if conta is None:
        raise NotFoundError("Conta não encontrada")
    status_anterior = conta.status
    svc = IdentidadeService(db)
    conta = await svc.mudar_status(conta, novo=payload.status, motivo=payload.motivo)
    await gravar_auditoria(
        db,
        acao="conta.mudar_status",
        recurso_tipo="conta",
        recurso_id=conta.id,
        conta_afetada_id=conta.id,
        payload={"de": status_anterior.value, "para": payload.status.value},
        motivo=payload.motivo,
        admin_id=current_user.id,
        request=request,
    )
    await db.commit()
    await db.refresh(conta)
    return conta


@router.post(
    "/{conta_id}/cortesia",
    response_model=dict,
    dependencies=[Depends(require_perfil_interno("superadmin", "gestor_comercial"))],
)
async def cortesia(
    conta_id: UUID,
    request: Request,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    conta = await db.get(Conta, conta_id)
    if conta is None:
        raise NotFoundError("Conta não encontrada")
    conta.cortesia_ativa = True
    await gravar_auditoria(
        db,
        acao="conta.cortesia_ativar",
        recurso_tipo="conta",
        recurso_id=conta.id,
        conta_afetada_id=conta.id,
        admin_id=current_user.id,
        request=request,
    )
    await db.commit()
    return {"ok": True, "conta_id": str(conta.id)}
