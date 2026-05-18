"""Catálogo — invalidação de cache Redis ao salvar."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import get_redis_cache
from app.models.atributo_especifico import AtributoComum
from app.models.categoria import Categoria
from app.models.subcategoria import Subcategoria
from app.models.tipo_material import TipoMaterial
from app.repositories.catalogo import (
    AtributoComumRepository,
    CategoriaRepository,
    SubcategoriaRepository,
    TipoMaterialRepository,
)


CACHE_KEY_CATEGORIAS = "catalogo:categorias_ativas"
CACHE_KEY_SUBCATEGORIAS = "catalogo:subcategorias:{categoria_id}"
CACHE_KEY_TIPOS = "catalogo:tipos:{subcategoria_id}"
CACHE_TTL_SECONDS = 300


class CatalogoService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.categorias = CategoriaRepository(db)
        self.subcategorias = SubcategoriaRepository(db)
        self.tipos_material = TipoMaterialRepository(db)
        self.atributos = AtributoComumRepository(db)
        self.cache = get_redis_cache()

    async def listar_categorias(self) -> list[Categoria]:
        return await self.categorias.listar_ativas()

    async def listar_subcategorias(self, categoria_id: UUID) -> list[Subcategoria]:
        return await self.subcategorias.listar_da_categoria(categoria_id)

    async def listar_tipos_material(self, subcategoria_id: UUID) -> list[TipoMaterial]:
        return await self.tipos_material.listar_da_subcategoria(subcategoria_id)

    async def criar_categoria(self, **kw) -> Categoria:
        c = Categoria(**kw)
        self.db.add(c)
        await self.db.flush()
        await self._invalidar_cache()
        return c

    async def atualizar_categoria(self, categoria: Categoria, **kw) -> Categoria:
        for k, v in kw.items():
            if v is not None:
                setattr(categoria, k, v)
        await self.db.flush()
        await self._invalidar_cache()
        return categoria

    async def criar_subcategoria(self, **kw) -> Subcategoria:
        s = Subcategoria(**kw)
        self.db.add(s)
        await self.db.flush()
        await self._invalidar_cache(categoria_id=s.categoria_id)
        return s

    async def atualizar_subcategoria(self, sub: Subcategoria, **kw) -> Subcategoria:
        for k, v in kw.items():
            if v is not None:
                setattr(sub, k, v)
        await self.db.flush()
        await self._invalidar_cache(categoria_id=sub.categoria_id)
        return sub

    async def criar_tipo_material(self, **kw) -> TipoMaterial:
        t = TipoMaterial(**kw)
        self.db.add(t)
        await self.db.flush()
        await self._invalidar_cache(subcategoria_id=t.subcategoria_id)
        return t

    async def atualizar_tipo_material(self, tipo: TipoMaterial, **kw) -> TipoMaterial:
        for k, v in kw.items():
            if v is not None:
                setattr(tipo, k, v)
        await self.db.flush()
        await self._invalidar_cache(subcategoria_id=tipo.subcategoria_id)
        return tipo

    async def _invalidar_cache(
        self,
        *,
        categoria_id: UUID | None = None,
        subcategoria_id: UUID | None = None,
    ) -> None:
        await self.cache.delete(CACHE_KEY_CATEGORIAS)
        if categoria_id:
            await self.cache.delete(CACHE_KEY_SUBCATEGORIAS.format(categoria_id=categoria_id))
        if subcategoria_id:
            await self.cache.delete(CACHE_KEY_TIPOS.format(subcategoria_id=subcategoria_id))


__all__ = ["CatalogoService"]
_ = AtributoComum  # mantém import vivo para referência
