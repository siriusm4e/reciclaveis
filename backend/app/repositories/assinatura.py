"""Repositórios — Plano, Assinatura, Fatura, Pagamento."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select, update

from app.models.assinatura import Assinatura
from app.models.enums import AssinaturaStatus, FaturaStatus, PapelTipo
from app.models.fatura import Fatura
from app.models.pagamento import Pagamento
from app.models.plano import Plano
from app.repositories.base import BaseRepository


class PlanoRepository(BaseRepository[Plano]):
    model = Plano

    async def listar_por_papel(self, papel: PapelTipo) -> list[Plano]:
        return list(
            await self.db.scalars(
                select(Plano).where(Plano.papel == papel, Plano.ativo.is_(True))
            )
        )

    async def gratuito_por_papel(self, papel: PapelTipo) -> Plano | None:
        return await self.db.scalar(
            select(Plano).where(
                Plano.papel == papel, Plano.gratuito.is_(True), Plano.ativo.is_(True)
            )
        )


class AssinaturaRepository(BaseRepository[Assinatura]):
    model = Assinatura

    async def listar_da_conta(self, conta_id: UUID) -> list[Assinatura]:
        return list(
            await self.db.scalars(
                select(Assinatura).where(Assinatura.conta_id == conta_id)
            )
        )

    async def get_do_papel(self, papel_id: UUID) -> Assinatura | None:
        return await self.db.scalar(
            select(Assinatura).where(Assinatura.papel_id == papel_id)
        )

    async def vencer_em_graca(self, *, dias_graca: int = 7) -> int:
        limite = datetime.now(tz=timezone.utc) - timedelta(days=dias_graca)
        stmt = (
            update(Assinatura)
            .where(
                Assinatura.status == AssinaturaStatus.EM_GRACA,
                Assinatura.em_graca_desde.is_not(None),
                Assinatura.em_graca_desde < limite,
            )
            .values(status=AssinaturaStatus.PAUSADA, pausada_desde=datetime.now(tz=timezone.utc))
            .execution_options(synchronize_session=False)
        )
        r = await self.db.execute(stmt)
        return r.rowcount or 0

    async def cancelar_pausadas_antigas(self, *, dias_pausada: int = 60) -> int:
        limite = datetime.now(tz=timezone.utc) - timedelta(days=dias_pausada)
        stmt = (
            update(Assinatura)
            .where(
                Assinatura.status == AssinaturaStatus.PAUSADA,
                Assinatura.pausada_desde.is_not(None),
                Assinatura.pausada_desde < limite,
            )
            .values(
                status=AssinaturaStatus.CANCELADA,
                cancelada_em=datetime.now(tz=timezone.utc),
            )
            .execution_options(synchronize_session=False)
        )
        r = await self.db.execute(stmt)
        return r.rowcount or 0

    async def listar_para_renovar(self) -> list[Assinatura]:
        return list(
            await self.db.scalars(
                select(Assinatura).where(
                    Assinatura.status == AssinaturaStatus.ATIVA,
                    Assinatura.data_renovacao < datetime.now(tz=timezone.utc),
                )
            )
        )


class FaturaRepository(BaseRepository[Fatura]):
    model = Fatura

    async def listar_da_assinatura(self, assinatura_id: UUID) -> list[Fatura]:
        return list(
            await self.db.scalars(
                select(Fatura)
                .where(Fatura.assinatura_id == assinatura_id)
                .order_by(Fatura.ciclo_inicio.desc())
            )
        )


class PagamentoRepository(BaseRepository[Pagamento]):
    model = Pagamento

    async def ultima_tentativa(self, fatura_id: UUID) -> Pagamento | None:
        return await self.db.scalar(
            select(Pagamento)
            .where(Pagamento.fatura_id == fatura_id)
            .order_by(Pagamento.tentativa.desc())
            .limit(1)
        )
