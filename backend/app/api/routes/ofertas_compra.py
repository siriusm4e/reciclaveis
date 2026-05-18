"""Rotas — OfertaCompra (com endpoint dedicado para Alerta Pago)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, require_papel_interno
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.conta import Conta
from app.models.enums import CondicaoForma, CondicaoLimpeza, CondicaoUmidade
from app.models.oferta_compra import OfertaCompra
from app.repositories.marketplace import OfertaCompraRepository
from app.schemas.marketplace import (
    AlertaPagoConfig,
    AlertaPagoResultado,
    OfertaCompraCreate,
    OfertaCompraRead,
    OfertaCompraUpdate,
)
from app.services.alerta_pago_service import AlertaPagoService
from app.services.marketplace_service import MarketplaceService

router = APIRouter(prefix="/api/ofertas-compra", tags=["marketplace:compra"])


@router.post(
    "/",
    response_model=OfertaCompraRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def criar(
    payload: OfertaCompraCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = MarketplaceService(db)
    oferta = await svc.criar_oferta_compra(
        conta_id=conta.id,
        papel_id=payload.papel_id,
        tipo_material_id=payload.tipo_material_id,
        titulo=payload.titulo,
        descricao=payload.descricao,
        especificacao=payload.especificacao,
        preco_paga=payload.preco_paga,
        unidade=payload.unidade,
        volume_min=payload.volume_min,
        volume_max=payload.volume_max,
        volume_minimo_kg=payload.volume_minimo_kg,
        condicao_limpeza=payload.condicao_limpeza,
        condicao_umidade=payload.condicao_umidade,
        condicao_forma=payload.condicao_forma,
        lat=payload.localizacao.lat,
        lng=payload.localizacao.lng,
        raio_km=payload.raio_km,
        retira=payload.retira,
        prazo_validade=payload.prazo_validade,
    )
    await db.commit()
    await db.refresh(oferta)
    return oferta


@router.get("/", response_model=list[OfertaCompraRead])
async def buscar(
    db: Annotated[AsyncSession, Depends(get_db)],
    subcategoria_id: UUID | None = Query(default=None),
    tipo_material_id: UUID | None = Query(default=None),
    lat: float | None = Query(default=None, ge=-90, le=90),
    lng: float | None = Query(default=None, ge=-180, le=180),
    raio_km: int | None = Query(default=None, ge=1, le=500, description="Entre 1 e 500 km"),
    # Filtro mútuo de volume: vendedor passa seu volume disponível; ofertas com
    # volume_minimo_kg > volume_disponivel_kg ficam ocultas.
    volume_disponivel_kg: float | None = Query(
        default=None,
        ge=0,
        description="Volume disponível do buscador em kg. Filtra ofertas com volume_minimo_kg > este valor.",
    ),
    condicao_limpeza: CondicaoLimpeza | None = Query(default=None),
    condicao_umidade: CondicaoUmidade | None = Query(default=None),
    condicao_forma: CondicaoForma | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    return await OfertaCompraRepository(db).buscar(
        subcategoria_id=subcategoria_id,
        tipo_material_id=tipo_material_id,
        lat=lat,
        lng=lng,
        raio_km=raio_km,
        volume_disponivel_kg=volume_disponivel_kg,
        condicao_limpeza=condicao_limpeza,
        condicao_umidade=condicao_umidade,
        condicao_forma=condicao_forma,
        limit=page_size,
        offset=(page - 1) * page_size,
    )


@router.get("/{oferta_id}", response_model=OfertaCompraRead)
async def detalhe(
    oferta_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OfertaCompra:
    oferta = await OfertaCompraRepository(db).get(oferta_id)
    if oferta is None:
        raise NotFoundError("Oferta não encontrada")
    return oferta


@router.patch("/{oferta_id}", response_model=OfertaCompraRead)
async def atualizar(
    oferta_id: UUID,
    payload: OfertaCompraUpdate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    repo = OfertaCompraRepository(db)
    oferta = await repo.get(oferta_id)
    if oferta is None:
        raise NotFoundError("Oferta não encontrada")
    if oferta.conta_id != conta.id:
        raise ForbiddenError("Oferta pertence a outra Conta")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(oferta, k, v)
    await db.commit()
    await db.refresh(oferta)
    return oferta


# ===== Alerta Pago (boost embutido na OfertaCompra) =====

@router.post(
    "/{oferta_id}/ativar-alerta-pago",
    response_model=AlertaPagoResultado,
    dependencies=[Depends(require_papel_interno("admin", "operador"))],
)
async def ativar_alerta_pago(
    oferta_id: UUID,
    payload: AlertaPagoConfig,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AlertaPagoResultado:
    repo = OfertaCompraRepository(db)
    oferta = await repo.get(oferta_id)
    if oferta is None:
        raise NotFoundError("Oferta não encontrada")
    if oferta.conta_id != conta.id:
        raise ForbiddenError("Oferta pertence a outra Conta")

    svc = AlertaPagoService(db)
    res = await svc.ativar(
        oferta_id=oferta_id,
        raio_km=payload.raio_km,
        duracao_horas=payload.duracao_horas,
        segmentacao=payload.segmentacao,
    )
    await db.commit()
    return AlertaPagoResultado(**res)
