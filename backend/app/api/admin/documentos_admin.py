"""Backoffice — Documentos (fila de aprovação)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_perfil_interno
from app.db.session import get_db
from app.models.usuario import Usuario
from app.repositories.documento import DocumentoRepository
from app.schemas.documentos import DocumentoRead, DocumentoRejeitar
from app.services.documento_service import DocumentoService
from app.utils.audit import gravar_auditoria

router = APIRouter(prefix="/api/admin/documentos", tags=["admin:documentos"])


@router.get(
    "/fila",
    response_model=list[DocumentoRead],
    dependencies=[Depends(require_perfil_interno("superadmin", "operador_atendimento"))],
)
async def fila(db: Annotated[AsyncSession, Depends(get_db)]):
    return await DocumentoRepository(db).listar_fila_pendente()


@router.post(
    "/{doc_id}/aprovar",
    response_model=DocumentoRead,
    dependencies=[Depends(require_perfil_interno("superadmin", "operador_atendimento"))],
)
async def aprovar(
    doc_id: UUID,
    request: Request,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = DocumentoService(db)
    doc = await svc.aprovar(doc_id, admin_id=current_user.id)
    await gravar_auditoria(
        db,
        acao="documento.aprovar",
        recurso_tipo="documento",
        recurso_id=doc.id,
        conta_afetada_id=doc.conta_id,
        admin_id=current_user.id,
        request=request,
    )
    await db.commit()
    await db.refresh(doc)
    return doc


@router.post(
    "/{doc_id}/rejeitar",
    response_model=DocumentoRead,
    dependencies=[Depends(require_perfil_interno("superadmin", "operador_atendimento"))],
)
async def rejeitar(
    doc_id: UUID,
    payload: DocumentoRejeitar,
    request: Request,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = DocumentoService(db)
    doc = await svc.rejeitar(doc_id, admin_id=current_user.id, motivo=payload.motivo)
    await gravar_auditoria(
        db,
        acao="documento.rejeitar",
        recurso_tipo="documento",
        recurso_id=doc.id,
        conta_afetada_id=doc.conta_id,
        motivo=payload.motivo,
        admin_id=current_user.id,
        request=request,
    )
    await db.commit()
    await db.refresh(doc)
    return doc
