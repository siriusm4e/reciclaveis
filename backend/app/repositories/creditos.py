"""Repositórios — TransacaoCredito (ledger imutável), PacoteCredito."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select

from app.models.pacote_credito import PacoteCredito
from app.models.transacao_credito import TransacaoCredito
from app.repositories.base import BaseRepository


class TransacaoCreditoRepository(BaseRepository[TransacaoCredito]):
    model = TransacaoCredito

    async def saldo(self, conta_id: UUID) -> int:
        """Projeção do saldo. Nunca é um campo direto na Conta."""
        return int(
            await self.db.scalar(
                select(func.coalesce(func.sum(TransacaoCredito.valor), 0)).where(
                    TransacaoCredito.conta_id == conta_id
                )
            )
            or 0
        )

    async def historico(
        self, conta_id: UUID, *, limit: int = 50, offset: int = 0
    ) -> list[TransacaoCredito]:
        return list(
            await self.db.scalars(
                select(TransacaoCredito)
                .where(TransacaoCredito.conta_id == conta_id)
                .order_by(TransacaoCredito.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
        )


class PacoteCreditoRepository(BaseRepository[PacoteCredito]):
    model = PacoteCredito

    async def listar_ativos(self) -> list[PacoteCredito]:
        return list(
            await self.db.scalars(
                select(PacoteCredito)
                .where(PacoteCredito.ativo.is_(True))
                .order_by(PacoteCredito.ordem)
            )
        )
