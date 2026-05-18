"""Rotas — TipoMaterial (público).

Expõe os atributos específicos do tipo + regulação documental herdada da Subcategoria pai.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.tipo_material import TipoMaterial
from app.repositories.catalogo import AtributoComumRepository
from app.schemas.catalogo import AtributoComumRead, TipoMaterialRead

router = APIRouter(prefix="/api/tipos", tags=["catalogo"])


@router.get("/{tipo_id}", response_model=TipoMaterialRead)
async def detalhe(
    tipo_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TipoMaterial:
    tipo = await db.scalar(select(TipoMaterial).where(TipoMaterial.id == tipo_id))
    if tipo is None:
        raise NotFoundError("Tipo de Material não encontrado")
    return tipo


@router.get("/{tipo_id}/atributos", response_model=dict)
async def listar_atributos(
    tipo_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    tipo = await db.scalar(
        select(TipoMaterial)
        .options(selectinload(TipoMaterial.subcategoria))
        .where(TipoMaterial.id == tipo_id)
    )
    if tipo is None:
        raise NotFoundError("Tipo de Material não encontrado")
    comuns = await AtributoComumRepository(db).listar_ativos()
    sub = tipo.subcategoria
    return {
        "comuns": [AtributoComumRead.model_validate(c).model_dump() for c in comuns],
        "especificos": tipo.atributos_especificos,
        "unidade_padrao": tipo.unidade_padrao,
        # Regulação herdada da Subcategoria intermediária
        "requer_validacao_documental": bool(sub and sub.requer_validacao_documental),
        "documentos_exigidos": list(sub.documentos_exigidos) if sub else [],
    }
