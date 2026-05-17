"""Backoffice — Analytics (preço médio, mapa, liquidez, exportação CSV)."""

from __future__ import annotations

import csv
import io
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_perfil_interno
from app.db.session import get_db
from app.schemas.analytics import (
    LiquidezPorSubcategoria,
    PrecoMedioPorTerritorio,
    PublicacoesAtivasPorSubcategoria,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(
    prefix="/api/admin/analytics",
    tags=["admin:analytics"],
    dependencies=[Depends(require_perfil_interno("superadmin", "gestor_comercial"))],
)


@router.get("/preco-medio", response_model=list[PrecoMedioPorTerritorio])
async def preco_medio(
    db: Annotated[AsyncSession, Depends(get_db)],
    subcategoria_id: str = Query(...),
    cidade: str | None = Query(default=None),
):
    from uuid import UUID

    svc = AnalyticsService(db)
    res = await svc.preco_referencia(subcategoria_id=UUID(subcategoria_id), cidade=cidade)
    return [
        PrecoMedioPorTerritorio(
            subcategoria_id=UUID(subcategoria_id),
            uf=None,
            cidade=cidade,
            amostra=res["amostra"],
            preco_medio=res["preco_medio"],
        )
    ]


@router.get("/publicacoes", response_model=list[PublicacoesAtivasPorSubcategoria])
async def publicacoes(db: Annotated[AsyncSession, Depends(get_db)]):
    svc = AnalyticsService(db)
    rows = await svc.publicacoes_ativas()
    return [PublicacoesAtivasPorSubcategoria(**r) for r in rows]


@router.get("/liquidez", response_model=list[LiquidezPorSubcategoria])
async def liquidez(db: Annotated[AsyncSession, Depends(get_db)]):
    svc = AnalyticsService(db)
    rows = await svc.liquidez()
    return [
        LiquidezPorSubcategoria(
            subcategoria_id=r["subcategoria_id"],
            nome="",
            ofertas=r["ofertas"],
            demandas=r["demandas"],
            razao=r["razao"],
        )
        for r in rows
    ]


@router.get("/exportar-csv")
async def exportar_csv(
    db: Annotated[AsyncSession, Depends(get_db)],
    relatorio: str = Query(default="liquidez", pattern=r"^(liquidez|publicacoes)$"),
):
    """CSV sem PII — apenas agregados por Subcategoria."""
    svc = AnalyticsService(db)
    if relatorio == "publicacoes":
        rows = await svc.publicacoes_ativas()
        headers = ["subcategoria_id", "nome", "total"]
    else:
        rows = await svc.liquidez()
        headers = ["subcategoria_id", "ofertas", "demandas", "razao"]

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=headers)
    writer.writeheader()
    for r in rows:
        writer.writerow({k: r.get(k, "") for k in headers})
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{relatorio}.csv"'},
    )
