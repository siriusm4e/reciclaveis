"""Repositórios — Oportunidade, Proposta."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update

from app.models.enums import OportunidadeStatus, PropostaStatus
from app.models.oportunidade import Oportunidade
from app.models.proposta import Proposta
from app.repositories.base import BaseRepository


class OportunidadeRepository(BaseRepository[Oportunidade]):
    model = Oportunidade

    async def listar_abertas(self) -> list[Oportunidade]:
        return list(
            await self.db.scalars(
                select(Oportunidade)
                .where(Oportunidade.status == OportunidadeStatus.ABERTA_PARA_PROPOSTA)
                .order_by(Oportunidade.prazo_submissao.asc())
            )
        )

    async def encerrar_prazo_vencido(self) -> int:
        stmt = (
            update(Oportunidade)
            .where(
                Oportunidade.status == OportunidadeStatus.ABERTA_PARA_PROPOSTA,
                Oportunidade.prazo_submissao < datetime.now(tz=timezone.utc),
            )
            .values(status=OportunidadeStatus.ENCERRADA)
            .execution_options(synchronize_session=False)
        )
        r = await self.db.execute(stmt)
        return r.rowcount or 0


class PropostaRepository(BaseRepository[Proposta]):
    model = Proposta

    async def listar_da_oportunidade(self, oportunidade_id: UUID) -> list[Proposta]:
        return list(
            await self.db.scalars(
                select(Proposta).where(Proposta.oportunidade_id == oportunidade_id)
            )
        )

    async def get_da_conta_na_oportunidade(
        self, conta_id: UUID, oportunidade_id: UUID
    ) -> Proposta | None:
        return await self.db.scalar(
            select(Proposta).where(
                Proposta.oportunidade_id == oportunidade_id,
                Proposta.conta_proponente_id == conta_id,
            )
        )

    async def expirar_pendentes_apos_encerramento(self, *, horas: int = 72) -> int:
        from datetime import timedelta

        limite = datetime.now(tz=timezone.utc) - timedelta(hours=horas)
        # Propostas SUBMETIDA cujas Oportunidades estão encerradas há mais de `horas`
        stmt = (
            update(Proposta)
            .where(
                Proposta.status == PropostaStatus.SUBMETIDA,
                Proposta.oportunidade_id.in_(
                    select(Oportunidade.id).where(
                        Oportunidade.status == OportunidadeStatus.ENCERRADA,
                        Oportunidade.updated_at < limite,
                    )
                ),
            )
            .values(status=PropostaStatus.EXPIRADA)
            .execution_options(synchronize_session=False)
        )
        r = await self.db.execute(stmt)
        return r.rowcount or 0
