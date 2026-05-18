"""Rotas públicas — listagem de TipoDocumento para selects no app.

CRUD administrativo continua em `api/admin/catalogo_admin.py`. Aqui só leitura.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.tipo_documento import TipoDocumento
from app.schemas.documentos import TipoDocumentoRead

router = APIRouter(prefix="/api/tipos-documento", tags=["documentos"])


@router.get("/", response_model=list[TipoDocumentoRead])
async def listar(
    db: Annotated[AsyncSession, Depends(get_db)],
    papel: str | None = Query(default=None, description="Slug do papel ativo (ex.: comprador). Filtra tipos aplicáveis."),
) -> list[TipoDocumento]:
    stmt = select(TipoDocumento).where(TipoDocumento.ativo.is_(True)).order_by(TipoDocumento.nome)
    rows = list(await db.scalars(stmt))
    if not papel:
        return rows
    # Lista vazia em papeis_aplicaveis significa "qualquer papel"
    return [t for t in rows if not t.papeis_aplicaveis or papel in t.papeis_aplicaveis]
