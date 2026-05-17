"""Repositórios — Negociacao, Mensagem, Avaliacao, VinculoDetectado."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, or_, select, update

from app.models.avaliacao import Avaliacao
from app.models.enums import NegociacaoStatus, PublicacaoTipo
from app.models.mensagem import Mensagem
from app.models.negociacao import Negociacao
from app.models.vinculo_detectado import VinculoDetectado
from app.repositories.base import BaseRepository


class NegociacaoRepository(BaseRepository[Negociacao]):
    model = Negociacao

    async def listar_da_conta(self, conta_id: UUID) -> list[Negociacao]:
        return list(
            await self.db.scalars(
                select(Negociacao)
                .where(
                    or_(
                        Negociacao.conta_vendedora_id == conta_id,
                        Negociacao.conta_compradora_id == conta_id,
                    )
                )
                .order_by(Negociacao.ultima_mensagem_em.desc().nullslast(), Negociacao.created_at.desc())
            )
        )

    async def existe_aberta(
        self,
        *,
        publicacao_id: UUID,
        publicacao_tipo: PublicacaoTipo,
        conta_vendedora_id: UUID,
        conta_compradora_id: UUID,
    ) -> Negociacao | None:
        return await self.db.scalar(
            select(Negociacao).where(
                Negociacao.publicacao_id == publicacao_id,
                Negociacao.publicacao_tipo == publicacao_tipo,
                Negociacao.conta_vendedora_id == conta_vendedora_id,
                Negociacao.conta_compradora_id == conta_compradora_id,
                Negociacao.status.in_(
                    [
                        NegociacaoStatus.ABERTA,
                        NegociacaoStatus.COMBINADA,
                        NegociacaoStatus.DISPUTADA,
                    ]
                ),
            )
        )

    async def expirar_inativas(self, *, dias: int = 14) -> int:
        limite = datetime.now(tz=timezone.utc) - timedelta(days=dias)
        # Critério: aberta E (sem ultima_mensagem OU ultima_mensagem < limite) E created_at < limite
        stmt = (
            update(Negociacao)
            .where(
                Negociacao.status == NegociacaoStatus.ABERTA,
                Negociacao.created_at < limite,
                or_(
                    Negociacao.ultima_mensagem_em.is_(None),
                    Negociacao.ultima_mensagem_em < limite,
                ),
            )
            .values(status=NegociacaoStatus.EXPIRADA)
            .execution_options(synchronize_session=False)
        )
        r = await self.db.execute(stmt)
        return r.rowcount or 0

    async def concluir_combinadas_antigas(self, *, dias: int = 7) -> int:
        limite = datetime.now(tz=timezone.utc) - timedelta(days=dias)
        stmt = (
            update(Negociacao)
            .where(
                Negociacao.status == NegociacaoStatus.COMBINADA,
                Negociacao.combinada_em.is_not(None),
                Negociacao.combinada_em < limite,
            )
            .values(status=NegociacaoStatus.CONCLUIDA)
            .execution_options(synchronize_session=False)
        )
        r = await self.db.execute(stmt)
        return r.rowcount or 0

    async def desfazer_sinalizacao_unilateral_expirada(self, *, horas: int = 48) -> int:
        """48h após sinalização sem confirmação do outro lado → volta a aberta."""
        limite = datetime.now(tz=timezone.utc) - timedelta(hours=horas)
        stmt = (
            update(Negociacao)
            .where(
                Negociacao.status == NegociacaoStatus.ABERTA,
                or_(
                    and_(
                        Negociacao.sinalizou_combinado_vendedor_em.is_not(None),
                        Negociacao.sinalizou_combinado_comprador_em.is_(None),
                        Negociacao.sinalizou_combinado_vendedor_em < limite,
                    ),
                    and_(
                        Negociacao.sinalizou_combinado_comprador_em.is_not(None),
                        Negociacao.sinalizou_combinado_vendedor_em.is_(None),
                        Negociacao.sinalizou_combinado_comprador_em < limite,
                    ),
                ),
            )
            .values(
                sinalizou_combinado_vendedor_em=None,
                sinalizou_combinado_comprador_em=None,
            )
            .execution_options(synchronize_session=False)
        )
        r = await self.db.execute(stmt)
        return r.rowcount or 0


class MensagemRepository(BaseRepository[Mensagem]):
    model = Mensagem

    async def listar_da_negociacao(self, negociacao_id: UUID) -> list[Mensagem]:
        return list(
            await self.db.scalars(
                select(Mensagem)
                .where(Mensagem.negociacao_id == negociacao_id)
                .order_by(Mensagem.created_at.asc())
            )
        )


class AvaliacaoRepository(BaseRepository[Avaliacao]):
    model = Avaliacao

    async def get_de_avaliador_na_negociacao(
        self, *, negociacao_id: UUID, avaliador_conta_id: UUID
    ) -> Avaliacao | None:
        return await self.db.scalar(
            select(Avaliacao).where(
                Avaliacao.negociacao_id == negociacao_id,
                Avaliacao.avaliador_conta_id == avaliador_conta_id,
            )
        )

    async def listar_visiveis_de_avaliado(self, avaliado_conta_id: UUID) -> list[Avaliacao]:
        return list(
            await self.db.scalars(
                select(Avaliacao).where(
                    Avaliacao.avaliado_conta_id == avaliado_conta_id,
                    Avaliacao.visivel.is_(True),
                    Avaliacao.removida.is_(False),
                )
            )
        )

    async def revelar_apos_janela(self, *, dias: int = 14) -> int:
        """Avaliações criadas há mais de `dias` (sem reciprocidade) → visíveis."""
        limite = datetime.now(tz=timezone.utc) - timedelta(days=dias)
        stmt = (
            update(Avaliacao)
            .where(
                Avaliacao.visivel.is_(False),
                Avaliacao.removida.is_(False),
                Avaliacao.created_at < limite,
            )
            .values(visivel=True)
            .execution_options(synchronize_session=False)
        )
        r = await self.db.execute(stmt)
        return r.rowcount or 0


class VinculoDetectadoRepository(BaseRepository[VinculoDetectado]):
    model = VinculoDetectado

    async def existe_entre(self, conta_a_id: UUID, conta_b_id: UUID) -> bool:
        result = await self.db.scalar(
            select(VinculoDetectado).where(
                or_(
                    and_(
                        VinculoDetectado.conta_a_id == conta_a_id,
                        VinculoDetectado.conta_b_id == conta_b_id,
                    ),
                    and_(
                        VinculoDetectado.conta_a_id == conta_b_id,
                        VinculoDetectado.conta_b_id == conta_a_id,
                    ),
                )
            )
        )
        return result is not None
