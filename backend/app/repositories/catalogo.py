"""Repositórios — Categoria, Subcategoria (intermediário), TipoMaterial (granular), AtributoComum."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.atributo_especifico import AtributoComum
from app.models.categoria import Categoria
from app.models.subcategoria import Subcategoria
from app.models.tipo_material import TipoMaterial
from app.repositories.base import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    model = Categoria

    async def listar_ativas(self) -> list[Categoria]:
        return list(
            await self.db.scalars(
                select(Categoria).where(Categoria.ativo.is_(True)).order_by(Categoria.ordem)
            )
        )

    async def get_by_slug(self, slug: str) -> Categoria | None:
        return await self.db.scalar(select(Categoria).where(Categoria.slug == slug))


class SubcategoriaRepository(BaseRepository[Subcategoria]):
    model = Subcategoria

    async def listar_da_categoria(self, categoria_id: UUID) -> list[Subcategoria]:
        return list(
            await self.db.scalars(
                select(Subcategoria)
                .where(Subcategoria.categoria_id == categoria_id, Subcategoria.ativo.is_(True))
                .order_by(Subcategoria.ordem)
            )
        )

    async def get_by_slug(self, categoria_id: UUID, slug: str) -> Subcategoria | None:
        return await self.db.scalar(
            select(Subcategoria).where(
                Subcategoria.categoria_id == categoria_id, Subcategoria.slug == slug
            )
        )


class TipoMaterialRepository(BaseRepository[TipoMaterial]):
    model = TipoMaterial

    async def listar_da_subcategoria(self, subcategoria_id: UUID) -> list[TipoMaterial]:
        return list(
            await self.db.scalars(
                select(TipoMaterial)
                .where(
                    TipoMaterial.subcategoria_id == subcategoria_id,
                    TipoMaterial.ativo.is_(True),
                )
                .order_by(TipoMaterial.ordem)
            )
        )

    async def get_by_slug(self, subcategoria_id: UUID, slug: str) -> TipoMaterial | None:
        return await self.db.scalar(
            select(TipoMaterial).where(
                TipoMaterial.subcategoria_id == subcategoria_id, TipoMaterial.slug == slug
            )
        )


class AtributoComumRepository(BaseRepository[AtributoComum]):
    model = AtributoComum

    async def listar_ativos(self) -> list[AtributoComum]:
        return list(
            await self.db.scalars(
                select(AtributoComum)
                .where(AtributoComum.ativo.is_(True))
                .order_by(AtributoComum.ordem)
            )
        )
