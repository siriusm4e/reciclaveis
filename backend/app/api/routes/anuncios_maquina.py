"""Rotas — AnuncioMaquina + endpoint de manutenção próxima."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, require_papel_interno
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.anuncio_maquina import AnuncioMaquina
from app.models.conta import Conta
from app.models.enums import AnuncioStatus, ModalidadeMaquina
from app.repositories.outros_anuncios import (
    AnuncioMaquinaRepository,
    AnuncioServicoRepository,
)
from app.schemas.marketplace import AnuncioMaquinaCreate, AnuncioMaquinaRead
from app.utils.geo import make_point_wkt

router = APIRouter(prefix="/api/anuncios-maquina", tags=["marketplace:maquinas"])


@router.post(
    "/",
    response_model=AnuncioMaquinaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def criar(
    payload: AnuncioMaquinaCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if payload.modalidade in (ModalidadeMaquina.ALUGUEL, ModalidadeMaquina.AMBOS) and not payload.disponibilidade:
        from app.core.exceptions import ValidationDomainError

        raise ValidationDomainError("Modalidade aluguel exige disponibilidade")

    obj = AnuncioMaquina(
        conta_id=conta.id,
        papel_id=payload.papel_id,
        categoria_equipamento=payload.categoria_equipamento,
        marca=payload.marca,
        modelo=payload.modelo,
        ano=payload.ano,
        capacidade=payload.capacidade,
        tensao=payload.tensao,
        descricao=payload.descricao,
        condicao=payload.condicao,
        modalidade=payload.modalidade,
        aceita_visita_tecnica=payload.aceita_visita_tecnica,
        disponibilidade=payload.disponibilidade,
        preco=payload.preco,
        documentacao_disponivel=payload.documentacao_disponivel,
        fotos=payload.fotos,
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


@router.get("/", response_model=list[AnuncioMaquinaRead])
async def buscar(
    db: Annotated[AsyncSession, Depends(get_db)],
    categoria_equipamento: str | None = Query(default=None),
    lat: float | None = Query(default=None, ge=-90, le=90),
    lng: float | None = Query(default=None, ge=-180, le=180),
    raio_km: int | None = Query(default=None, ge=1, le=500),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    return await AnuncioMaquinaRepository(db).buscar(
        categoria_equipamento=categoria_equipamento,
        lat=lat,
        lng=lng,
        raio_km=raio_km,
        limit=page_size,
        offset=(page - 1) * page_size,
    )


@router.get("/{anuncio_id}", response_model=AnuncioMaquinaRead)
async def detalhe(
    anuncio_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    obj = await AnuncioMaquinaRepository(db).get(anuncio_id)
    if obj is None:
        raise NotFoundError("Máquina não encontrada")
    return obj


@router.get("/{anuncio_id}/manutencao-proxima", response_model=list)
async def manutencao_proxima(
    anuncio_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    obj = await AnuncioMaquinaRepository(db).get(anuncio_id)
    if obj is None:
        raise NotFoundError("Máquina não encontrada")
    prestadores = await AnuncioServicoRepository(db).manutencao_proxima(obj.lat, obj.lng, raio_km=50)
    return [
        {
            "id": p.id,
            "conta_id": p.conta_id,
            "tipo_servico": p.tipo_servico,
            "raio_operacional_km": p.raio_operacional_km,
            "preco": p.preco,
        }
        for p in prestadores
    ]


_ = ForbiddenError
