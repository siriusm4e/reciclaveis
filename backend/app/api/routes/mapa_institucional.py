"""Rotas — Mapa institucional (restrito a Órgão Público pelo escopo territorial)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa
from app.core.exceptions import ForbiddenError
from app.db.session import get_db
from app.models.conta import Conta
from app.schemas.institucional import MapaInstitucionalCelula, MapaInstitucionalResposta
from app.services.institucional_service import InstitucionalService

router = APIRouter(prefix="/api/mapa-institucional", tags=["institucional"])


@router.get("/", response_model=MapaInstitucionalResposta)
async def consultar(
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
    ibge: str = Query(..., pattern=r"^\d{7}$"),
):
    svc = InstitucionalService(db)
    await svc.valida_acesso_mapa(conta=conta, ibge=ibge)
    celulas = await svc.mapa_municipio(ibge)
    return MapaInstitucionalResposta(
        territorio=f"municipio:{ibge}",
        celulas=[
            MapaInstitucionalCelula(
                bairro=c["bairro"],
                cidade="",
                uf="",
                ibge_municipio=c["ibge_municipio"],
                anuncios_ativos=c["anuncios_ativos"],
                pedidos_abertos=c["pedidos_abertos"],
                campanhas_ativas=c["campanhas_ativas"],
            )
            for c in celulas
        ],
    )


_ = ForbiddenError
