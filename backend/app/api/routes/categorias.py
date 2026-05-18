"""Rotas — Categorias e Subcategorias (público).

Endpoints encadeados para os 3 dropdowns do formulário de anúncio:
    /api/categorias/                          → lista categorias ativas
    /api/categorias/{id}/subcategorias        → lista subcategorias da categoria
    /api/subcategorias/{id}/tipos             → lista TiposMaterial da subcategoria
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.categoria import Categoria
from app.models.subcategoria import Subcategoria
from app.models.tipo_material import TipoMaterial
from app.repositories.catalogo import (
    CategoriaRepository,
    SubcategoriaRepository,
    TipoMaterialRepository,
)
from app.schemas.catalogo import CategoriaRead, SubcategoriaRead, TipoMaterialRead

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


@sub_router.get("/{subcategoria_id}/tipos", response_model=list[TipoMaterialRead])
async def listar_tipos_da_subcategoria(
    subcategoria_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TipoMaterial]:
    return await TipoMaterialRepository(db).listar_da_subcategoria(subcategoria_id)
