"""Rotas — Oportunidade + Proposta."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, require_papel_interno
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.conta import Conta
from app.models.oportunidade import Oportunidade
from app.repositories.oportunidade import OportunidadeRepository, PropostaRepository
from app.schemas.negociacao import (
    OportunidadeCreate,
    OportunidadeRead,
    PropostaCreate,
    PropostaRead,
)
from app.services.oportunidade_service import OportunidadeService

router = APIRouter(prefix="/api/oportunidades", tags=["oportunidades"])


@router.get("/", response_model=list[OportunidadeRead])
async def listar(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await OportunidadeRepository(db).listar_abertas()


@router.get("/{op_id}", response_model=OportunidadeRead)
async def detalhe(
    op_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    op = await OportunidadeRepository(db).get(op_id)
    if op is None:
        raise NotFoundError("Oportunidade não encontrada")
    return op


@router.post(
    "/",
    response_model=OportunidadeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def criar(
    payload: OportunidadeCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = OportunidadeService(db)
    op = await svc.criar(
        conta_id=conta.id,
        titulo=payload.titulo,
        descricao=payload.descricao,
        subcategoria_id=payload.subcategoria_id,
        tipo=payload.tipo,
        documentos_exigidos=payload.documentos_exigidos,
        prazo_submissao=payload.prazo_submissao,
        valor_estimado=payload.valor_estimado,
    )
    await db.commit()
    await db.refresh(op)
    return op


@router.post(
    "/{op_id}/propostas",
    response_model=PropostaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def submeter_proposta(
    op_id: UUID,
    payload: PropostaCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = OportunidadeService(db)
    p = await svc.submeter_proposta(
        oportunidade_id=op_id,
        conta_proponente_id=conta.id,
        valor=payload.valor,
        condicoes=payload.condicoes,
        documentos_anexos=payload.documentos_anexos,
    )
    await db.commit()
    await db.refresh(p)
    return p


@router.get(
    "/{op_id}/propostas",
    response_model=list[PropostaRead],
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def listar_propostas(
    op_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    op = await OportunidadeRepository(db).get(op_id)
    if op is None:
        raise NotFoundError("Oportunidade não encontrada")
    if op.conta_id != conta.id:
        raise ForbiddenError("Apenas a Conta criadora vê as Propostas")
    return await PropostaRepository(db).listar_da_oportunidade(op_id)


@router.post(
    "/{op_id}/declarar-vencedor",
    response_model=OportunidadeRead,
    dependencies=[Depends(require_papel_interno("admin"))],
)
async def declarar_vencedor(
    op_id: UUID,
    proposta_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    op = await OportunidadeRepository(db).get(op_id)
    if op is None:
        raise NotFoundError("Oportunidade não encontrada")
    if op.conta_id != conta.id:
        raise ForbiddenError("Apenas a Conta criadora declara vencedor")
    svc = OportunidadeService(db)
    op = await svc.declarar_vencedor(oportunidade=op, proposta_id=proposta_id)
    await db.commit()
    await db.refresh(op)
    return op


@router.post(
    "/{op_id}/encerrar",
    response_model=OportunidadeRead,
    dependencies=[Depends(require_papel_interno("admin"))],
)
async def encerrar(
    op_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    op = await OportunidadeRepository(db).get(op_id)
    if op is None or op.conta_id != conta.id:
        raise NotFoundError("Oportunidade não encontrada")
    svc = OportunidadeService(db)
    op = await svc.encerrar(op)
    await db.commit()
    await db.refresh(op)
    return op


_ = Oportunidade  # keep import alive
