"""Rotas — Categorias (público)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.atributo_especifico import AtributoComum
from app.models.categoria import Categoria
from app.models.subcategoria import Subcategoria
from app.repositories.catalogo import (
    AtributoComumRepository,
    CategoriaRepository,
    SubcategoriaRepository,
)
from app.schemas.catalogo import AtributoComumRead, CategoriaRead, SubcategoriaRead

router = APIRouter(prefix="/api/categorias", tags=["catalogo"])


@router.get("/", response_model=list[CategoriaRead])
async def listar_categorias(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Categoria]:
    return await CategoriaRepository(db).listar_ativas()


@router.get("/{categoria_id}/subcategorias", response_model=list[SubcategoriaRead])
async def listar_subcategorias(
    categoria_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Subcategoria]:
    return await SubcategoriaRepository(db).listar_da_categoria(categoria_id)


sub_router = APIRouter(prefix="/api/subcategorias", tags=["catalogo"])


@sub_router.get("/{subcategoria_id}/atributos", response_model=dict)
async def listar_atributos(
    subcategoria_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    sub = await SubcategoriaRepository(db).get(subcategoria_id)
    if sub is None:
        raise NotFoundError("Subcategoria não encontrada")
    comuns = await AtributoComumRepository(db).listar_ativos()
    return {
        "comuns": [AtributoComumRead.model_validate(c).model_dump() for c in comuns],
        "especificos": sub.atributos_especificos,
        "requer_validacao_documental": sub.requer_validacao_documental,
        "documentos_exigidos": sub.documentos_exigidos,
    }


_ = AtributoComum  # keep import alive
