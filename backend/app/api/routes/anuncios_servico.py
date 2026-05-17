"""Rotas — AnuncioServico."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, require_papel_interno
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.anuncio_servico import AnuncioServico
from app.models.conta import Conta
from app.models.enums import AnuncioStatus
from app.repositories.outros_anuncios import AnuncioServicoRepository
from app.schemas.marketplace import AnuncioServicoCreate, AnuncioServicoRead
from app.utils.geo import make_point_wkt

router = APIRouter(prefix="/api/anuncios-servico", tags=["marketplace:servicos"])


@router.post(
    "/",
    response_model=AnuncioServicoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def criar(
    payload: AnuncioServicoCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    obj = AnuncioServico(
        conta_id=conta.id,
        papel_id=payload.papel_id,
        tipo_servico=payload.tipo_servico,
        descricao=payload.descricao,
        raio_operacional_km=payload.raio_operacional_km,
        unidade_cobranca=payload.unidade_cobranca,
        preco=payload.preco,
        requer_visita_tecnica=payload.requer_visita_tecnica,
        disponibilidade=payload.disponibilidade,
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


@router.get("/", response_model=list[AnuncioServicoRead])
async def buscar(
    db: Annotated[AsyncSession, Depends(get_db)],
    tipo_servico: str | None = Query(default=None),
    lat: float | None = Query(default=None, ge=-90, le=90),
    lng: float | None = Query(default=None, ge=-180, le=180),
    raio_km: int | None = Query(default=None, ge=1, le=500),
):
    return await AnuncioServicoRepository(db).buscar(
        tipo_servico=tipo_servico, lat=lat, lng=lng, raio_km=raio_km
    )


@router.get("/{anuncio_id}", response_model=AnuncioServicoRead)
async def detalhe(
    anuncio_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    obj = await AnuncioServicoRepository(db).get(anuncio_id)
    if obj is None:
        raise NotFoundError("Serviço não encontrado")
    return obj
