"""Backoffice — Categorias, Subcategorias, TiposDocumento."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_perfil_interno
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.repositories.catalogo import (
    CategoriaRepository,
    SubcategoriaRepository,
)
from app.repositories.documento import TipoDocumentoRepository
from app.schemas.catalogo import (
    CategoriaCreate,
    CategoriaRead,
    CategoriaUpdate,
    SubcategoriaCreate,
    SubcategoriaRead,
    SubcategoriaUpdate,
)
from app.schemas.documentos import (
    TipoDocumentoCreate,
    TipoDocumentoRead,
    TipoDocumentoUpdate,
)
from app.services.catalogo_service import CatalogoService

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:catalogo"],
    dependencies=[Depends(require_perfil_interno("superadmin", "operador_atendimento"))],
)


# === Categorias ===

@router.post("/categorias/", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
async def criar_categoria(
    payload: CategoriaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = CatalogoService(db)
    c = await svc.criar_categoria(**payload.model_dump())
    await db.commit()
    return c


@router.patch("/categorias/{categoria_id}", response_model=CategoriaRead)
async def atualizar_categoria(
    categoria_id: UUID,
    payload: CategoriaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = CategoriaRepository(db)
    c = await repo.get(categoria_id)
    if c is None:
        raise NotFoundError("Categoria não encontrada")
    svc = CatalogoService(db)
    c = await svc.atualizar_categoria(c, **payload.model_dump(exclude_unset=True))
    await db.commit()
    return c


# === Subcategorias ===

@router.post(
    "/subcategorias/",
    response_model=SubcategoriaRead,
    status_code=status.HTTP_201_CREATED,
)
async def criar_subcategoria(
    payload: SubcategoriaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = CatalogoService(db)
    s = await svc.criar_subcategoria(**payload.model_dump())
    await db.commit()
    return s


@router.patch("/subcategorias/{subcategoria_id}", response_model=SubcategoriaRead)
async def atualizar_subcategoria(
    subcategoria_id: UUID,
    payload: SubcategoriaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = SubcategoriaRepository(db)
    s = await repo.get(subcategoria_id)
    if s is None:
        raise NotFoundError("Subcategoria não encontrada")
    svc = CatalogoService(db)
    s = await svc.atualizar_subcategoria(s, **payload.model_dump(exclude_unset=True))
    await db.commit()
    return s


# === Tipos de Documento ===

@router.post(
    "/tipos-documento/",
    response_model=TipoDocumentoRead,
    status_code=status.HTTP_201_CREATED,
)
async def criar_tipo(
    payload: TipoDocumentoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = TipoDocumentoRepository(db)
    from app.models.tipo_documento import TipoDocumento

    t = TipoDocumento(**payload.model_dump())
    await repo.create(t)
    await db.commit()
    return t


@router.patch("/tipos-documento/{tipo_id}", response_model=TipoDocumentoRead)
async def atualizar_tipo(
    tipo_id: UUID,
    payload: TipoDocumentoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = TipoDocumentoRepository(db)
    t = await repo.get(tipo_id)
    if t is None:
        raise NotFoundError("Tipo de Documento não encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    await db.commit()
    return t
