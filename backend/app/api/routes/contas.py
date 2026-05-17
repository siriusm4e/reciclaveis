"""Rotas — Conta (criar, ler, atualizar)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, get_current_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.conta import Conta
from app.models.usuario import Usuario
from app.repositories.conta import ContaRepository
from app.schemas.identidade import ContaCreate, ContaRead, ContaUpdate
from app.services.identidade_service import IdentidadeService

router = APIRouter(prefix="/api/contas", tags=["contas"])


@router.post("/", response_model=ContaRead, status_code=status.HTTP_201_CREATED)
async def criar_conta(
    payload: ContaCreate,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Conta:
    svc = IdentidadeService(db)
    conta = await svc.criar_conta(
        usuario=current_user,
        tipo=payload.tipo,
        nome_publico=payload.nome_publico,
        cnpj=payload.cnpj,
        escopo_territorial=payload.escopo_territorial,
    )
    await svc.detectar_vinculos(conta)
    await db.commit()
    await db.refresh(conta)
    return conta


@router.get("/", response_model=list[ContaRead])
async def listar_contas_do_usuario(
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Conta]:
    return await ContaRepository(db).listar_para_usuario(current_user.id)


@router.get("/{conta_id}", response_model=ContaRead)
async def get_conta(
    conta_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Conta:
    if conta.id != conta_id:
        # Permitir leitura básica de Conta diferente (perfil público) — mas só conta ativa atualiza
        c = await ContaRepository(db).get(conta_id)
        if c is None:
            raise NotFoundError("Conta não encontrada")
        return c
    return conta


@router.patch("/{conta_id}", response_model=ContaRead)
async def atualizar_conta(
    conta_id: UUID,
    payload: ContaUpdate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Conta:
    if conta.id != conta_id:
        raise NotFoundError("Conta não encontrada")
    svc = IdentidadeService(db)
    conta = await svc.atualizar_conta(
        conta,
        nome_publico=payload.nome_publico,
        foto_perfil_path=payload.foto_perfil_path,
        escopo_territorial=payload.escopo_territorial,
    )
    await db.commit()
    await db.refresh(conta)
    return conta
