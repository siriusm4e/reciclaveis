"""Rotas — Documentos da Conta autenticada."""

from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, require_papel_interno
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.conta import Conta
from app.repositories.documento import DocumentoRepository
from app.schemas.documentos import DocumentoRead
from app.services.documento_service import DocumentoService

router = APIRouter(prefix="/api/documentos", tags=["documentos"])


@router.get("/", response_model=list[DocumentoRead])
async def listar(
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await DocumentoRepository(db).listar_da_conta(conta.id)


@router.get("/{doc_id}", response_model=DocumentoRead)
async def get_documento(
    doc_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    doc = await DocumentoRepository(db).get(doc_id)
    if doc is None or doc.conta_id != conta.id:
        raise NotFoundError("Documento não encontrado")
    return doc


@router.post(
    "/",
    response_model=DocumentoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def upload(
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
    tipo_documento_id: Annotated[UUID, Form()],
    arquivo: Annotated[UploadFile, File()],
    estabelecimento_id: Annotated[UUID | None, Form()] = None,
    numero: Annotated[str | None, Form()] = None,
    data_emissao: Annotated[date | None, Form()] = None,
    data_vencimento: Annotated[date | None, Form()] = None,
):
    svc = DocumentoService(db)
    doc = await svc.upload(
        conta_id=conta.id,
        tipo_documento_id=tipo_documento_id,
        file_obj=arquivo.file,
        declared_filename=arquivo.filename,
        estabelecimento_id=estabelecimento_id,
        numero=numero,
        data_emissao=data_emissao,
        data_vencimento=data_vencimento,
    )
    await db.commit()
    await db.refresh(doc)
    return doc


@router.post(
    "/{doc_id}/renovar",
    response_model=DocumentoRead,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def renovar(
    doc_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
    arquivo: Annotated[UploadFile, File()],
    numero: Annotated[str | None, Form()] = None,
    data_emissao: Annotated[date | None, Form()] = None,
    data_vencimento: Annotated[date | None, Form()] = None,
):
    repo = DocumentoRepository(db)
    anterior = await repo.get(doc_id)
    if anterior is None or anterior.conta_id != conta.id:
        raise NotFoundError("Documento original não encontrado")

    svc = DocumentoService(db)
    novo = await svc.upload(
        conta_id=conta.id,
        tipo_documento_id=anterior.tipo_documento_id,
        file_obj=arquivo.file,
        declared_filename=arquivo.filename,
        estabelecimento_id=anterior.estabelecimento_id,
        numero=numero,
        data_emissao=data_emissao,
        data_vencimento=data_vencimento,
    )
    novo.substitui_id = anterior.id
    await db.commit()
    await db.refresh(novo)
    return novo
