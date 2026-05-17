"""Repositórios — AnuncioVenda, OfertaCompra, AssinaturaAlerta."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, update

from app.models.anuncio_venda import AnuncioVenda
from app.models.assinatura_alerta import AssinaturaAlerta
from app.models.enums import AnuncioVendaStatus, OfertaCompraStatus
from app.models.oferta_compra import OfertaCompra
from app.repositories.base import BaseRepository
from app.utils.geo import st_dwithin_geography


class AnuncioVendaRepository(BaseRepository[AnuncioVenda]):
    model = AnuncioVenda

    async def buscar(
        self,
        *,
        categoria_id: UUID | None = None,
        subcategoria_id: UUID | None = None,
        lat: float | None = None,
        lng: float | None = None,
        raio_km: int | None = None,
        preco_min: Decimal | None = None,
        preco_max: Decimal | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AnuncioVenda]:
        from app.models.subcategoria import Subcategoria

        stmt = select(AnuncioVenda).where(AnuncioVenda.status == AnuncioVendaStatus.PUBLICADO)
        if categoria_id:
            stmt = stmt.join(Subcategoria, Subcategoria.id == AnuncioVenda.subcategoria_id).where(
                Subcategoria.categoria_id == categoria_id
            )
        if subcategoria_id:
            stmt = stmt.where(AnuncioVenda.subcategoria_id == subcategoria_id)
        if preco_min is not None:
            stmt = stmt.where(AnuncioVenda.preco_pretendido >= preco_min)
        if preco_max is not None:
            stmt = stmt.where(AnuncioVenda.preco_pretendido <= preco_max)
        if lat is not None and lng is not None and raio_km is not None:
            stmt = stmt.where(st_dwithin_geography(AnuncioVenda.geom_pub, lat, lng, raio_km))
        stmt = stmt.order_by(AnuncioVenda.created_at.desc()).limit(limit).offset(offset)
        return list(await self.db.scalars(stmt))

    async def listar_da_conta(self, conta_id: UUID) -> list[AnuncioVenda]:
        return list(
            await self.db.scalars(
                select(AnuncioVenda).where(AnuncioVenda.conta_id == conta_id)
            )
        )

    async def expirar_vencidos(self) -> int:
        stmt = (
            update(AnuncioVenda)
            .where(
                AnuncioVenda.status.in_(
                    [AnuncioVendaStatus.PUBLICADO, AnuncioVendaStatus.PAUSADO]
                ),
                AnuncioVenda.prazo_validade < datetime.now(tz=timezone.utc),
            )
            .values(status=AnuncioVendaStatus.EXPIRADO)
            .execution_options(synchronize_session=False)
        )
        r = await self.db.execute(stmt)
        return r.rowcount or 0


class OfertaCompraRepository(BaseRepository[OfertaCompra]):
    model = OfertaCompra

    async def buscar(
        self,
        *,
        subcategoria_id: UUID | None = None,
        lat: float | None = None,
        lng: float | None = None,
        raio_km: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[OfertaCompra]:
        stmt = select(OfertaCompra).where(OfertaCompra.status == OfertaCompraStatus.PUBLICADA)
        if subcategoria_id:
            stmt = stmt.where(OfertaCompra.subcategoria_id == subcategoria_id)
        if lat is not None and lng is not None and raio_km is not None:
            stmt = stmt.where(st_dwithin_geography(OfertaCompra.geom, lat, lng, raio_km))
        stmt = stmt.order_by(OfertaCompra.created_at.desc()).limit(limit).offset(offset)
        return list(await self.db.scalars(stmt))

    async def listar_da_conta(self, conta_id: UUID) -> list[OfertaCompra]:
        return list(
            await self.db.scalars(
                select(OfertaCompra).where(OfertaCompra.conta_id == conta_id)
            )
        )

    async def expirar_vencidos(self) -> int:
        stmt = (
            update(OfertaCompra)
            .where(
                OfertaCompra.status.in_(
                    [OfertaCompraStatus.PUBLICADA, OfertaCompraStatus.PAUSADA]
                ),
                OfertaCompra.prazo_validade < datetime.now(tz=timezone.utc),
            )
            .values(status=OfertaCompraStatus.EXPIRADA)
            .execution_options(synchronize_session=False)
        )
        r = await self.db.execute(stmt)
        return r.rowcount or 0

    async def desativar_boost_expirado(self) -> int:
        stmt = (
            update(OfertaCompra)
            .where(
                OfertaCompra.boost_ativo.is_(True),
                OfertaCompra.boost_fim.is_not(None),
                OfertaCompra.boost_fim < datetime.now(tz=timezone.utc),
            )
            .values(boost_ativo=False)
            .execution_options(synchronize_session=False)
        )
        r = await self.db.execute(stmt)
        return r.rowcount or 0


class AssinaturaAlertaRepository(BaseRepository[AssinaturaAlerta]):
    model = AssinaturaAlerta

    async def listar_da_conta(self, conta_id: UUID) -> list[AssinaturaAlerta]:
        return list(
            await self.db.scalars(
                select(AssinaturaAlerta).where(AssinaturaAlerta.conta_id == conta_id)
            )
        )
