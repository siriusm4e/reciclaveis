"""Analytics — agregados sem PII e preço de referência."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anuncio_venda import AnuncioVenda
from app.models.enums import AnuncioVendaStatus
from app.models.oferta_compra import OfertaCompra
from app.models.subcategoria import Subcategoria


MIN_AMOSTRA_PRECO = 5


class AnalyticsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def preco_referencia(
        self, *, subcategoria_id: UUID, cidade: str | None = None
    ) -> dict:
        # AnúnciosVenda publicados servem como amostra de preço
        # (não usamos Negociação por sigilo do valor combinado).
        stmt = select(
            func.count(AnuncioVenda.id), func.avg(AnuncioVenda.preco_pretendido)
        ).where(
            AnuncioVenda.subcategoria_id == subcategoria_id,
            AnuncioVenda.status == AnuncioVendaStatus.PUBLICADO,
        )
        # cidade — futuramente filtrar via join com estabelecimento próximo / IBGE
        amostra, media = (await self.db.execute(stmt)).first() or (0, None)
        if int(amostra) < MIN_AMOSTRA_PRECO:
            return {
                "subcategoria_id": subcategoria_id,
                "cidade": cidade,
                "amostra": int(amostra),
                "preco_medio": None,
            }
        return {
            "subcategoria_id": subcategoria_id,
            "cidade": cidade,
            "amostra": int(amostra),
            "preco_medio": Decimal(media or 0),
        }

    async def publicacoes_ativas(self) -> list[dict]:
        rows = await self.db.execute(
            select(
                Subcategoria.id,
                Subcategoria.nome,
                func.count(AnuncioVenda.id),
            )
            .join(AnuncioVenda, AnuncioVenda.subcategoria_id == Subcategoria.id)
            .where(AnuncioVenda.status == AnuncioVendaStatus.PUBLICADO)
            .group_by(Subcategoria.id, Subcategoria.nome)
            .order_by(func.count(AnuncioVenda.id).desc())
        )
        return [{"subcategoria_id": sid, "nome": nome, "total": int(total)} for sid, nome, total in rows]

    async def liquidez(self) -> list[dict]:
        sub_ids = await self.db.scalars(select(Subcategoria.id))
        out = []
        for sid in sub_ids:
            ofertas = int(
                await self.db.scalar(
                    select(func.count()).select_from(AnuncioVenda).where(
                        AnuncioVenda.subcategoria_id == sid,
                        AnuncioVenda.status == AnuncioVendaStatus.PUBLICADO,
                    )
                )
                or 0
            )
            demandas = int(
                await self.db.scalar(
                    select(func.count()).select_from(OfertaCompra).where(
                        OfertaCompra.subcategoria_id == sid,
                        OfertaCompra.status == "publicada",  # OfertaCompraStatus.PUBLICADA.value
                    )
                )
                or 0
            )
            razao = (ofertas / demandas) if demandas else None
            out.append(
                {
                    "subcategoria_id": sid,
                    "ofertas": ofertas,
                    "demandas": demandas,
                    "razao": razao,
                }
            )
        return out


__all__ = ["AnalyticsService", "MIN_AMOSTRA_PRECO"]
