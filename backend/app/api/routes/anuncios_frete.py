"""Rotas — AnuncioFrete."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, require_papel_interno
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.anuncio_frete import AnuncioFrete
from app.models.conta import Conta
from app.models.enums import AnuncioStatus
from app.repositories.outros_anuncios import AnuncioFreteRepository
from app.schemas.marketplace import AnuncioFreteCreate, AnuncioFreteRead
from app.utils.geo import make_point_wkt

router = APIRouter(prefix="/api/anuncios-frete", tags=["marketplace:fretes"])


@router.post(
    "/",
    response_model=AnuncioFreteRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def criar(
    payload: AnuncioFreteCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    obj = AnuncioFrete(
        conta_id=conta.id,
        papel_id=payload.papel_id,
        tipo_veiculo=payload.tipo_veiculo,
        capacidade_t=payload.capacidade_t,
        capacidade_m3=payload.capacidade_m3,
        tara=payload.tara,
        raio_operacional_km=payload.raio_operacional_km,
        categorias_residuo_aceitas=payload.categorias_residuo_aceitas,
        licencas=payload.licencas,
        emite_nf=payload.emite_nf,
        lat=payload.localizacao.lat,
        lng=payload.localizacao.lng,
        geom=make_point_wkt(payload.localizacao.lat, payload.localizacao.lng),
        prazo_validade=payload.prazo_validade,
        status=AnuncioStatus.PUBLICADO,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("/", response_model=list[AnuncioFreteRead])
async def buscar(
    db: Annotated[AsyncSession, Depends(get_db)],
    tipo_veiculo: str | None = Query(default=None),
    categoria_aceita: str | None = Query(default=None, description="Slug de Categoria de resíduo"),
    lat: float | None = Query(default=None, ge=-90, le=90),
    lng: float | None = Query(default=None, ge=-180, le=180),
    raio_km: int | None = Query(default=None, ge=1, le=2000),
):
    return await AnuncioFreteRepository(db).buscar(
        tipo_veiculo=tipo_veiculo,
        categoria_aceita=categoria_aceita,
        lat=lat,
        lng=lng,
        raio_km=raio_km,
    )


@router.get("/{anuncio_id}", response_model=AnuncioFreteRead)
async def detalhe(
    anuncio_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    obj = await AnuncioFreteRepository(db).get(anuncio_id)
    if obj is None:
        raise NotFoundError("Frete não encontrado")
    return obj
