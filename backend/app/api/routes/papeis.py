"""Rotas — PapelAtivado e Estabelecimento da Conta."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_conta_ativa, require_papel_interno
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.conta import Conta
from app.models.papel import PapelAtivado
from app.repositories.conta import EstabelecimentoRepository, PapelRepository
from app.schemas.identidade import (
    EstabelecimentoCreate,
    EstabelecimentoRead,
    PapelCreate,
    PapelRead,
    PapelUpdate,
)
from app.services.identidade_service import IdentidadeService

router_papeis = APIRouter(prefix="/api/contas/{conta_id}/papeis", tags=["papeis"])
router_est = APIRouter(prefix="/api/contas/{conta_id}/estabelecimentos", tags=["estabelecimentos"])


@router_papeis.get("/", response_model=list[PapelRead])
async def listar_papeis(
    conta_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[PapelAtivado]:
    return await PapelRepository(db).listar_da_conta(conta_id)


@router_papeis.post(
    "/",
    response_model=PapelRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin"))],
)
async def ativar_papel(
    conta_id: UUID,
    payload: PapelCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PapelAtivado:
    svc = IdentidadeService(db)
    p = await svc.ativar_papel(conta=conta, papel=payload.papel, dados=payload.dados_complementares)
    await db.commit()
    await db.refresh(p)
    return p


@router_papeis.patch(
    "/{papel_id}",
    response_model=PapelRead,
    dependencies=[Depends(require_papel_interno("admin"))],
)
async def atualizar_papel(
    conta_id: UUID,
    papel_id: UUID,
    payload: PapelUpdate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PapelAtivado:
    repo = PapelRepository(db)
    p = await repo.get(papel_id)
    if p is None or p.conta_id != conta.id:
        raise NotFoundError("Papel não encontrado")
    svc = IdentidadeService(db)
    p = await svc.atualizar_papel(papel=p, dados=payload.dados_complementares, status=payload.status)
    await db.commit()
    return p


# ===== Estabelecimentos =====

@router_est.get("/", response_model=list[EstabelecimentoRead])
async def listar_estabelecimentos(
    conta_id: UUID,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    rows = await EstabelecimentoRepository(db).listar_da_conta(conta_id)
    return [_geom_to_read(r) for r in rows]


@router_est.post(
    "/",
    response_model=EstabelecimentoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_papel_interno("admin"))],
)
async def criar_estabelecimento(
    conta_id: UUID,
    payload: EstabelecimentoCreate,
    conta: Annotated[Conta, Depends(get_conta_ativa)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    svc = IdentidadeService(db)
    est = await svc.criar_estabelecimento(
        conta=conta,
        nome=payload.nome,
        cep=payload.cep,
        logradouro=payload.logradouro,
        numero=payload.numero,
        complemento=payload.complemento,
        bairro=payload.bairro,
        cidade=payload.cidade,
        uf=payload.uf,
        ibge_municipio=payload.ibge_municipio,
        lat=payload.localizacao.lat,
        lng=payload.localizacao.lng,
    )
    await db.commit()
    await db.refresh(est)
    return _geom_to_read(est)


def _geom_to_read(est) -> dict:
    """Converte ORM com geom PostGIS → dict com lat/lng explícitos."""
    from geoalchemy2.shape import to_shape

    point = to_shape(est.geom) if est.geom is not None else None
    return {
        "id": est.id,
        "created_at": est.created_at,
        "updated_at": est.updated_at,
        "conta_id": est.conta_id,
        "nome": est.nome,
        "cep": est.cep,
        "logradouro": est.logradouro,
        "numero": est.numero,
        "complemento": est.complemento,
        "bairro": est.bairro,
        "cidade": est.cidade,
        "uf": est.uf,
        "ibge_municipio": est.ibge_municipio,
        "lat": point.y if point else 0.0,
        "lng": point.x if point else 0.0,
    }
