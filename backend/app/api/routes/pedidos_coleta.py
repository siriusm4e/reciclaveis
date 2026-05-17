"""Rotas — PedidoColetaPublica."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.conta import Conta
from app.repositories.institucional import PedidoColetaRepository
from app.schemas.institucional import (
    PedidoColetaCreate,
    PedidoColetaRead,
    PedidoColetaStatusUpdate,
)
from app.services.institucional_service import InstitucionalService

router = APIRouter(prefix="/api/pedidos-coleta", tags=["institucional"])


@router.post(
    "/", response_model=PedidoColetaRead, status_code=status.HTTP_201_CREATED
)
async def criar(
    payload: PedidoColetaCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = InstitucionalService(db)
    p = await svc.criar_pedido(
        conta_solicitante_id=conta.id,
        bairro=payload.bairro,
        cidade=payload.cidade,
        uf=payload.uf,
        ibge=payload.ibge_municipio,
        tipo_residuo=payload.tipo_residuo,
        foto_path=payload.foto_path,
        quantidade=payload.quantidade_estimada,
        descricao=payload.descricao,
        lat=payload.localizacao.lat,
        lng=payload.localizacao.lng,
    )
    await db.commit()
    await db.refresh(p)
    return p


@router.get("/", response_model=list[PedidoColetaRead])
async def listar(
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = PedidoColetaRepository(db)
    # Solicitante vê os seus + Prefeitura (se Conta tem papel PREFEITURA) vê os do município
    do_solicitante = await repo.listar_do_solicitante(conta.id)
    da_prefeitura = await repo.listar_da_prefeitura(conta.id)
    seen = set()
    out = []
    for p in (*do_solicitante, *da_prefeitura):
        if p.id in seen:
            continue
        seen.add(p.id)
        out.append(p)
    return out


@router.patch("/{pedido_id}/status", response_model=PedidoColetaRead)
async def atualizar_status(
    pedido_id: UUID,
    payload: PedidoColetaStatusUpdate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = PedidoColetaRepository(db)
    p = await repo.get(pedido_id)
    if p is None:
        raise NotFoundError("Pedido não encontrado")
    svc = InstitucionalService(db)
    p = await svc.atualizar_status(pedido=p, novo=payload.status, prefeitura_conta_id=conta.id)
    await db.commit()
    await db.refresh(p)
    return p


@router.post("/{pedido_id}/contestar", response_model=PedidoColetaRead)
async def contestar(
    pedido_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = PedidoColetaRepository(db)
    p = await repo.get(pedido_id)
    if p is None:
        raise NotFoundError("Pedido não encontrado")
    svc = InstitucionalService(db)
    p = await svc.contestar_fechamento(pedido=p, conta_id=conta.id)
    await db.commit()
    await db.refresh(p)
    return p
