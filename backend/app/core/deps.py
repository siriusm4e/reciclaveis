"""Dependencies FastAPI — auth, sessão de Conta ativa, escopo de Papel."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.redis_client import is_conta_banned, is_jti_blocked
from app.core.security import TOKEN_TYPE_ACCESS, decode_token
from app.db.session import get_db

# tokenUrl é apenas para o Swagger UI; o backend não exige form-urlencoded em /login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=True)


# === Usuário ===

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Resolve o Usuario autenticado pelo bearer access token."""
    from app.models.usuario import Usuario  # import tardio evita ciclo

    payload = decode_token(token, expected_type=TOKEN_TYPE_ACCESS)
    jti = payload.get("jti", "")
    if await is_jti_blocked(jti):
        raise UnauthorizedError("Sessão revogada")

    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError) as e:
        raise UnauthorizedError("Token inválido") from e

    user = await db.scalar(select(Usuario).where(Usuario.id == user_id))
    if user is None or not user.ativo:
        raise UnauthorizedError("Usuário não encontrado ou desativado")
    return user


CurrentUser = Annotated["object", Depends(get_current_user)]


# === Conta ativa ===

async def get_conta_ativa(
    current_user: Annotated["object", Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    x_conta_id: Annotated[str | None, Header(alias="X-Conta-Id")] = None,
):
    """Resolve a Conta ativa do usuário (vinda do header `X-Conta-Id`).

    Se omitido e o usuário tiver exatamente uma Conta vinculada, usa essa.
    """
    from app.models.conta import Conta, ContaStatus
    from app.models.membro import Membro

    if x_conta_id:
        try:
            conta_id = UUID(x_conta_id)
        except ValueError as e:
            raise UnauthorizedError("X-Conta-Id inválido") from e
    else:
        memberships = (
            await db.scalars(
                select(Membro.conta_id).where(Membro.usuario_id == current_user.id)
            )
        ).all()
        if len(memberships) != 1:
            raise ForbiddenError(
                "Conta ativa não selecionada", details={"memberships": len(memberships)}
            )
        conta_id = memberships[0]

    membership = await db.scalar(
        select(Membro).where(Membro.usuario_id == current_user.id, Membro.conta_id == conta_id)
    )
    if membership is None:
        raise ForbiddenError("Usuário não pertence à Conta informada")

    conta = await db.scalar(select(Conta).where(Conta.id == conta_id))
    if conta is None:
        raise ForbiddenError("Conta não encontrada")
    if await is_conta_banned(str(conta.id)):
        raise ForbiddenError("Conta banida")
    if conta.status not in (ContaStatus.ATIVA, ContaStatus.PENDENTE, ContaStatus.EM_REVISAO):
        raise ForbiddenError(f"Conta com status {conta.status.value}")

    return conta


CurrentConta = Annotated["object", Depends(get_conta_ativa)]


# === Permissão por papel_interno em Membro (admin/operador/leitor da Conta) ===

def require_papel_interno(*papeis: str):
    """Exige que o Membro do usuário na Conta ativa tenha um dos `papeis` listados."""

    async def _dep(
        current_user: Annotated["object", Depends(get_current_user)],
        conta=Depends(get_conta_ativa),
        db: Annotated[AsyncSession, Depends(get_db)] = ...,
    ):
        from app.models.membro import Membro

        membro = await db.scalar(
            select(Membro).where(
                Membro.usuario_id == current_user.id, Membro.conta_id == conta.id
            )
        )
        if membro is None or membro.papel_interno.value not in papeis:
            raise ForbiddenError(
                "Permissão insuficiente",
                details={"requerido": list(papeis), "atual": getattr(membro, "papel_interno", None)},
            )
        return membro

    return _dep


# === Backoffice — exige perfil_interno (superadmin / operador_atendimento / ...) ===

def require_perfil_interno(*perfis: str):
    """Exige que o usuário esteja vinculado a um PerfilInterno do backoffice."""

    async def _dep(
        current_user: Annotated["object", Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)] = ...,
    ):
        from app.models.perfil_interno import PerfilInterno

        perfil = await db.scalar(
            select(PerfilInterno).where(PerfilInterno.usuario_id == current_user.id)
        )
        if perfil is None or perfil.tipo.value not in perfis:
            raise ForbiddenError(
                "Acesso ao backoffice negado",
                details={"requerido": list(perfis), "atual": getattr(perfil, "tipo", None)},
            )
        return perfil

    return _dep
