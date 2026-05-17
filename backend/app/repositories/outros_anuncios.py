"""Repositórios — AnuncioMaquina, AnuncioServico, AnuncioFrete."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update

from app.models.anuncio_frete import AnuncioFrete
from app.models.anuncio_maquina import AnuncioMaquina
from app.models.anuncio_servico import AnuncioServico
from app.models.enums import AnuncioStatus
from app.repositories.base import BaseRepository
from app.utils.geo import st_dwithin_geography


class AnuncioMaquinaRepository(BaseRepository[AnuncioMaquina]):
    model = AnuncioMaquina

    async def buscar(
        self,
        *,
        categoria_equipamento: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
        raio_km: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AnuncioMaquina]:
        stmt = select(AnuncioMaquina).where(AnuncioMaquina.status == AnuncioStatus.PUBLICADO)
        if categoria_equipamento:
            stmt = stmt.where(AnuncioMaquina.categoria_equipamento == categoria_equipamento)
        if lat is not None and lng is not None and raio_km is not None:
            stmt = stmt.where(st_dwithin_geography(AnuncioMaquina.geom, lat, lng, raio_km))
        stmt = stmt.order_by(AnuncioMaquina.created_at.desc()).limit(limit).offset(offset)
        return list(await self.db.scalars(stmt))


class AnuncioServicoRepository(BaseRepository[AnuncioServico]):
    model = AnuncioServico

    async def buscar(
        self,
        *,
        tipo_servico: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
        raio_km: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AnuncioServico]:
        stmt = select(AnuncioServico).where(AnuncioServico.status == AnuncioStatus.PUBLICADO)
        if tipo_servico:
            stmt = stmt.where(AnuncioServico.tipo_servico == tipo_servico)
        if lat is not None and lng is not None and raio_km is not None:
            stmt = stmt.where(st_dwithin_geography(AnuncioServico.geom, lat, lng, raio_km))
        stmt = stmt.order_by(AnuncioServico.created_at.desc()).limit(limit).offset(offset)
        return list(await self.db.scalars(stmt))

    async def manutencao_proxima(
        self, lat: float, lng: float, *, raio_km: int = 50
    ) -> list[AnuncioServico]:
        """Prestadores de manutenção em até `raio_km` do equipamento."""
        stmt = (
            select(AnuncioServico)
            .where(
                AnuncioServico.status == AnuncioStatus.PUBLICADO,
                AnuncioServico.tipo_servico.ilike("%manutencao%"),
                st_dwithin_geography(AnuncioServico.geom, lat, lng, raio_km),
            )
            .order_by(AnuncioServico.created_at.desc())
        )
        return list(await self.db.scalars(stmt))


class AnuncioFreteRepository(BaseRepository[AnuncioFrete]):
    model = AnuncioFrete

    async def buscar(
        self,
        *,
        tipo_veiculo: str | None = None,
        categoria_aceita: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
        raio_km: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AnuncioFrete]:
        from sqlalchemy.dialects.postgresql import JSONB
        from sqlalchemy import cast, literal

        stmt = select(AnuncioFrete).where(AnuncioFrete.status == AnuncioStatus.PUBLICADO)
        if tipo_veiculo:
            stmt = stmt.where(AnuncioFrete.tipo_veiculo == tipo_veiculo)
        if categoria_aceita:
            # JSONB ? operador: categoria_aceita está na lista categorias_residuo_aceitas
            stmt = stmt.where(
                AnuncioFrete.categorias_residuo_aceitas.op("?")(categoria_aceita)
            )
        if lat is not None and lng is not None and raio_km is not None:
            stmt = stmt.where(st_dwithin_geography(AnuncioFrete.geom, lat, lng, raio_km))
        stmt = stmt.order_by(AnuncioFrete.created_at.desc()).limit(limit).offset(offset)
        return list(await self.db.scalars(stmt))


# Expiração genérica de anúncios (máquina/serviço/frete)
async def expirar_anuncios_status_generico(db, model) -> int:  # noqa: ANN001
    stmt = (
        update(model)
        .where(
            model.status.in_([AnuncioStatus.PUBLICADO, AnuncioStatus.PAUSADO]),
            model.prazo_validade < datetime.now(tz=timezone.utc),
        )
        .values(status=AnuncioStatus.EXPIRADO)
        .execution_options(synchronize_session=False)
    )
    r = await db.execute(stmt)
    return r.rowcount or 0
