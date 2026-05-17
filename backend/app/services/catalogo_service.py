"""Catálogo — invalidação de cache Redis ao salvar."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import get_redis_cache
from app.models.atributo_especifico import AtributoComum
from app.models.categoria import Categoria
from app.models.subcategoria import Subcategoria
from app.repositories.catalogo import (
    AtributoComumRepository,
    CategoriaRepository,
    SubcategoriaRepository,
)


CACHE_KEY_CATEGORIAS = "catalogo:categorias_ativas"
CACHE_KEY_SUBCATEGORIAS = "catalogo:subcategorias:{categoria_id}"
CACHE_TTL_SECONDS = 300


class CatalogoService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.categorias = CategoriaRepository(db)
        self.subcategorias = SubcategoriaRepository(db)
        self.atributos = AtributoComumRepository(db)
        self.cache = get_redis_cache()

    async def listar_categorias(self) -> list[Categoria]:
        # Sem cache em primeira versão para evitar serializar ORM; cache pode entrar
        # com Pydantic Read no service que consome (idem subcategorias).
        return await self.categorias.listar_ativas()

    async def listar_subcategorias(self, categoria_id: UUID) -> list[Subcategoria]:
        return await self.subcategorias.listar_da_categoria(categoria_id)

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

    async def _invalidar_cache(self, *, categoria_id: UUID | None = None) -> None:
        await self.cache.delete(CACHE_KEY_CATEGORIAS)
        if categoria_id:
            await self.cache.delete(CACHE_KEY_SUBCATEGORIAS.format(categoria_id=categoria_id))


__all__ = ["CatalogoService"]
_ = AtributoComum  # mantém import vivo para referência
