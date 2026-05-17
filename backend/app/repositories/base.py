"""BaseRepository genérico com CRUD assíncrono."""

from __future__ import annotations

from typing import Any, Generic, Sequence, TypeVar
from uuid import UUID

from sqlalchemy import delete as sa_delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """CRUD genérico — não comita; o caller controla a unidade de trabalho."""

    model: type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, id_: UUID) -> ModelT | None:
        return await self.db.get(self.model, id_)

    async def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        order_by: Any = None,
        where: Sequence[Any] | None = None,
    ) -> list[ModelT]:
        stmt = select(self.model)
        if where:
            stmt = stmt.where(*where)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.scalars(stmt)
        return list(result)

    async def count(self, *, where: Sequence[Any] | None = None) -> int:
        stmt = select(func.count()).select_from(self.model)
        if where:
            stmt = stmt.where(*where)
        return int(await self.db.scalar(stmt) or 0)

    async def create(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def update(self, obj: ModelT, **attrs: Any) -> ModelT:
        for k, v in attrs.items():
            setattr(obj, k, v)
        await self.db.flush()
        return obj

    async def delete(self, id_: UUID) -> int:
        result = await self.db.execute(sa_delete(self.model).where(self.model.id == id_))
        await self.db.flush()
        return result.rowcount or 0
