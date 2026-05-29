"""Rotas — perfil do Usuario autenticado."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.exceptions import ConflictError, UnauthorizedError, ValidationDomainError
from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.auth import AlterarEmailRequest, AlterarSenhaRequest, UsuarioPublic
from app.schemas.common import OkResponse

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


async def _load_com_perfil(db: AsyncSession, usuario_id) -> Usuario:
    """Recarrega o usuário com perfil_interno — UsuarioPublic serializa esse
    relacionamento, que é lazy e dispararia I/O fora do contexto async."""
    return await db.scalar(
        select(Usuario)
        .where(Usuario.id == usuario_id)
        .options(selectinload(Usuario.perfil_interno))
    )


@router.get("/me", response_model=UsuarioPublic)
async def me(
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Usuario:
    return await _load_com_perfil(db, current_user.id)


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
    return await _load_com_perfil(db, current_user.id)


@router.patch("/me/email", response_model=UsuarioPublic)
async def alterar_email(
    payload: AlterarEmailRequest,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Usuario:
    """Troca o e-mail de login — exige a senha atual e e-mail não usado."""
    if not verify_password(payload.senha_atual, current_user.senha_hash):
        raise UnauthorizedError("Senha atual incorreta")

    novo = str(payload.novo_email).lower()
    if novo == current_user.email.lower():
        raise ValidationDomainError("O novo e-mail é igual ao atual")

    existing = await db.scalar(select(Usuario).where(Usuario.email == novo))
    if existing is not None:
        raise ConflictError("E-mail já cadastrado")

    current_user.email = novo
    await db.commit()
    return await _load_com_perfil(db, current_user.id)


@router.post("/me/senha", response_model=OkResponse)
async def alterar_senha(
    payload: AlterarSenhaRequest,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OkResponse:
    """Troca a senha — exige a senha atual."""
    if not verify_password(payload.senha_atual, current_user.senha_hash):
        raise UnauthorizedError("Senha atual incorreta")
    if verify_password(payload.nova_senha, current_user.senha_hash):
        raise ValidationDomainError("A nova senha é igual à atual")

    current_user.senha_hash = hash_password(payload.nova_senha)
    await db.commit()
    return OkResponse(ok=True)


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
