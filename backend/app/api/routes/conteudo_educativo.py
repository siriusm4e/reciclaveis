"""Rotas — ConteudoEducativo (público; admin tem CRUD em api/admin)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.repositories.conteudo import ConteudoEducativoRepository
from app.schemas.conteudo import ConteudoEducativoRead

router = APIRouter(prefix="/api/conteudo", tags=["conteudo"])


@router.get("/", response_model=list[ConteudoEducativoRead])
async def listar(
    db: Annotated[AsyncSession, Depends(get_db)],
    papel: str | None = Query(default=None),
    categoria: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    return await ConteudoEducativoRepository(db).listar_publicados(
        papel_slug=papel,
        categoria_slug=categoria,
        limit=page_size,
        offset=(page - 1) * page_size,
    )


@router.get("/{conteudo_id}", response_model=ConteudoEducativoRead)
async def detalhe(
    conteudo_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    obj = await ConteudoEducativoRepository(db).get(conteudo_id)
    if obj is None or not obj.publicado:
        raise NotFoundError("Conteúdo não encontrado")
    return obj
