"""Rotas — AnuncioVenda (criar, listar, buscar, detalhe, atualizar, replicar)."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, get_current_user, require_papel_interno
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.anuncio_venda import AnuncioVenda
from app.models.conta import Conta
from app.models.enums import CondicaoForma, CondicaoLimpeza, CondicaoUmidade
from app.repositories.marketplace import AnuncioVendaRepository
from app.schemas.marketplace import (
    AnuncioVendaCreate,
    AnuncioVendaRead,
    AnuncioVendaUpdate,
)
from app.services.marketplace_service import MarketplaceService

router = APIRouter(prefix="/api/anuncios-venda", tags=["marketplace:venda"])


@router.post(
    "/",
    response_model=AnuncioVendaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def criar(
    payload: AnuncioVendaCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AnuncioVenda:
    if payload.fotos and len(payload.fotos) > 3:
        raise HTTPException(status_code=422, detail="Máximo de 3 fotos por anúncio")
    svc = MarketplaceService(db)
    anuncio = await svc.criar_anuncio_venda(
        conta_id=conta.id,
        papel_id=payload.papel_id,
        tipo_material_id=payload.tipo_material_id,
        atributos=payload.atributos,
        condicao_limpeza=payload.condicao_limpeza,
        condicao_umidade=payload.condicao_umidade,
        condicao_forma=payload.condicao_forma,
        lat_real=payload.localizacao_real.lat,
        lng_real=payload.localizacao_real.lng,
        territorio=payload.territorio,
        preco_pretendido=payload.preco_pretendido,
        unidade=payload.unidade,
        volume_estimado=payload.volume_estimado,
        frequencia=payload.frequencia,
        intervalo_geracao=payload.intervalo_geracao,
        prazo_validade=payload.prazo_validade,
        fotos=payload.fotos,
        aceita_alerta_pago_de_terceiros=payload.aceita_alerta_pago_de_terceiros,
    )
    await db.commit()
    await db.refresh(anuncio)
    return anuncio


@router.get("/", response_model=list[AnuncioVendaRead])
async def buscar(
    db: Annotated[AsyncSession, Depends(get_db)],
    categoria_id: UUID | None = Query(default=None),
    subcategoria_id: UUID | None = Query(default=None),
    tipo_material_id: UUID | None = Query(default=None),
    lat: float | None = Query(default=None, ge=-90, le=90),
    lng: float | None = Query(default=None, ge=-180, le=180),
    raio_km: int | None = Query(default=None, ge=1, le=500, description="Entre 1 e 500 km"),
    preco_min: Decimal | None = Query(default=None),
    preco_max: Decimal | None = Query(default=None),
    volume_minimo_kg: float | None = Query(
        default=None,
        ge=0,
        description="Filtro mútuo: oculta vendedores com volume_estimado abaixo deste número.",
    ),
    condicao_limpeza: CondicaoLimpeza | None = Query(default=None),
    condicao_umidade: CondicaoUmidade | None = Query(default=None),
    condicao_forma: CondicaoForma | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    return await AnuncioVendaRepository(db).buscar(
        categoria_id=categoria_id,
        subcategoria_id=subcategoria_id,
        tipo_material_id=tipo_material_id,
        lat=lat,
        lng=lng,
        raio_km=raio_km,
        preco_min=preco_min,
        preco_max=preco_max,
        volume_minimo_kg=volume_minimo_kg,
        condicao_limpeza=condicao_limpeza,
        condicao_umidade=condicao_umidade,
        condicao_forma=condicao_forma,
        limit=page_size,
        offset=(page - 1) * page_size,
    )


@router.get("/{anuncio_id}", response_model=AnuncioVendaRead)
async def detalhe(
    anuncio_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AnuncioVenda:
    anuncio = await AnuncioVendaRepository(db).get(anuncio_id)
    if anuncio is None:
        raise NotFoundError("Anúncio não encontrado")
    # incrementa visualizações best-effort (não falha se rollback)
    try:
        anuncio.visualizacoes += 1
        await db.commit()
        # Recarrega para que `updated_at` (atualizado pelo onupdate=func.now())
        # esteja disponível durante a serialização sem lazy load async.
        await db.refresh(anuncio)
    except Exception:
        await db.rollback()
    return anuncio


@router.patch("/{anuncio_id}", response_model=AnuncioVendaRead)
async def atualizar(
    anuncio_id: UUID,
    payload: AnuncioVendaUpdate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if payload.fotos is not None and len(payload.fotos) > 3:
        raise HTTPException(status_code=422, detail="Máximo de 3 fotos por anúncio")
    repo = AnuncioVendaRepository(db)
    anuncio = await repo.get(anuncio_id)
    if anuncio is None:
        raise NotFoundError("Anúncio não encontrado")
    if anuncio.conta_id != conta.id:
        raise ForbiddenError("Anúncio pertence a outra Conta")
    svc = MarketplaceService(db)
    await svc.atualizar_anuncio(anuncio, **payload.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(anuncio)
    return anuncio


@router.post(
    "/{anuncio_id}/replicar",
    response_model=AnuncioVendaRead,
    status_code=status.HTTP_201_CREATED,
)
async def replicar(
    anuncio_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = AnuncioVendaRepository(db)
    anuncio = await repo.get(anuncio_id)
    if anuncio is None or anuncio.conta_id != conta.id:
        raise NotFoundError("Anúncio não encontrado")
    svc = MarketplaceService(db)
    novo = await svc.replicar_anuncio(anuncio)
    await db.commit()
    await db.refresh(novo)
    return novo


_ = get_current_user  # mantém import vivo
