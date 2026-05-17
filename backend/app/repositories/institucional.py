"""Repositórios — PedidoColetaPublica, CampanhaPublica."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.campanha_publica import CampanhaPublica
from app.models.enums import CampanhaStatus, PedidoColetaStatus
from app.models.pedido_coleta_publica import PedidoColetaPublica
from app.repositories.base import BaseRepository


class PedidoColetaRepository(BaseRepository[PedidoColetaPublica]):
    model = PedidoColetaPublica

    async def listar_da_prefeitura(self, prefeitura_conta_id: UUID) -> list[PedidoColetaPublica]:
        return list(
            await self.db.scalars(
                select(PedidoColetaPublica)
                .where(PedidoColetaPublica.prefeitura_conta_id == prefeitura_conta_id)
                .order_by(PedidoColetaPublica.created_at.desc())
            )
        )

    async def listar_do_solicitante(self, conta_id: UUID) -> list[PedidoColetaPublica]:
        return list(
            await self.db.scalars(
                select(PedidoColetaPublica).where(
                    PedidoColetaPublica.conta_solicitante_id == conta_id
                )
            )
        )

    async def por_municipio_status(
        self, ibge: str, status: PedidoColetaStatus | None = None
    ) -> list[PedidoColetaPublica]:
        stmt = select(PedidoColetaPublica).where(PedidoColetaPublica.ibge_municipio == ibge)
        if status:
            stmt = stmt.where(PedidoColetaPublica.status == status)
        return list(await self.db.scalars(stmt))


class CampanhaRepository(BaseRepository[CampanhaPublica]):
    model = CampanhaPublica

    async def listar_publicadas_para_municipio(self, ibge: str) -> list[CampanhaPublica]:
        return list(
            await self.db.scalars(
                select(CampanhaPublica).where(
                    CampanhaPublica.status == CampanhaStatus.PUBLICADA,
                    CampanhaPublica.ibge_municipio == ibge,
                )
            )
        )

    async def listar_da_conta(self, conta_id: UUID) -> list[CampanhaPublica]:
        return list(
            await self.db.scalars(
                select(CampanhaPublica).where(
                    CampanhaPublica.conta_organizadora_id == conta_id
                )
            )
        )
