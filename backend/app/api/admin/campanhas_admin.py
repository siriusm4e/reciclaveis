"""Backoffice — Campanhas (gestor_institucional)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_perfil_interno
from app.db.session import get_db
from app.repositories.institucional import CampanhaRepository
from app.schemas.institucional import CampanhaRead

router = APIRouter(
    prefix="/api/admin/campanhas",
    tags=["admin:campanhas"],
    dependencies=[Depends(require_perfil_interno("superadmin", "gestor_institucional"))],
)


@router.get("/", response_model=list[CampanhaRead])
async def listar(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    return await CampanhaRepository(db).list(limit=page_size, offset=(page - 1) * page_size)
