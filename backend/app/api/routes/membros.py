"""Rotas — Membros e Convites de Conta PJ."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, get_current_user, require_papel_interno
from app.db.session import get_db
from app.models.conta import Conta
from app.models.membro import Membro
from app.models.usuario import Usuario
from app.repositories.conta import ConviteRepository, MembroRepository
from app.schemas.common import OkResponse
from app.schemas.identidade import ConviteCreate, ConviteRead, MembroRead
from app.services.identidade_service import IdentidadeService

router = APIRouter(prefix="/api/contas/{conta_id}/membros", tags=["membros"])


@router.get("/", response_model=list[MembroRead])
async def listar_membros(
    conta_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _admin: Annotated[Membro, Depends(require_papel_interno("admin", "operador", "leitor"))] = None,
) -> list[Membro]:
    return await MembroRepository(db).listar_da_conta(conta_id)


@router.post(
    "/",
    response_model=ConviteRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin"))],
)
async def convidar_membro(
    conta_id: UUID,
    payload: ConviteCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = IdentidadeService(db)
    convite = await svc.convidar_membro(
        conta=conta,
        email=str(payload.email),
        papel_interno=payload.papel_interno,
        convidado_por_usuario_id=current_user.id,
    )
    await db.commit()
    await db.refresh(convite)
    return convite


@router.delete(
    "/{membro_id}",
    response_model=OkResponse,
    dependencies=[Depends(require_papel_interno("admin"))],
)
async def remover_membro(
    conta_id: UUID,
    membro_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OkResponse:
    svc = IdentidadeService(db)
    await svc.remover_membro(conta_id=conta_id, membro_id=membro_id)
    await db.commit()
    return OkResponse(ok=True)
