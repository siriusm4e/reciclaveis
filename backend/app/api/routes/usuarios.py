"""Rotas — perfil do Usuario autenticado."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.exceptions import ValidationDomainError
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.auth import UsuarioPublic
from app.schemas.common import OkResponse

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.get("/me", response_model=UsuarioPublic)
async def me(current_user: Annotated[Usuario, Depends(get_current_user)]) -> Usuario:
    return current_user


@router.patch("/me", response_model=UsuarioPublic)
async def update_me(
    payload: dict,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Usuario:
    permitidos = {"nome_completo", "telefone", "foto_path"}
    for k, v in payload.items():
        if k not in permitidos:
            raise ValidationDomainError(f"Campo {k} não pode ser atualizado por esta rota")
        setattr(current_user, k, v)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/me/excluir", response_model=OkResponse, status_code=status.HTTP_202_ACCEPTED)
async def pedir_exclusao(
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OkResponse:
    """LGPD — registra pedido. Anonimização ocorre após graça (settings.LGPD_GRACA_EXCLUSAO_DIAS)."""
    from datetime import datetime, timezone

    if current_user.pedido_exclusao_em is None:
        current_user.pedido_exclusao_em = datetime.now(tz=timezone.utc)
        await db.commit()
    return OkResponse(ok=True)


_ = settings  # mantém import vivo
