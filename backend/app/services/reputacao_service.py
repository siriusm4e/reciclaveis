"""Reputação — média por Papel, janela cega, bloqueio por VinculoDetectado."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    VinculoDetectadoError,
)
from app.models.avaliacao import Avaliacao
from app.models.enums import NegociacaoStatus, PapelTipo
from app.models.negociacao import Negociacao
from app.repositories.negociacao import (
    AvaliacaoRepository,
    NegociacaoRepository,
    VinculoDetectadoRepository,
)


JANELA_AVALIACAO_DIAS = 14


class ReputacaoService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.avaliacoes = AvaliacaoRepository(db)
        self.negociacoes = NegociacaoRepository(db)
        self.vinculos = VinculoDetectadoRepository(db)

    async def avaliar(
        self,
        *,
        negociacao_id: UUID,
        avaliador_conta_id: UUID,
        nota: int,
        papel_avaliado: PapelTipo,
        subnotas: dict,
        comentario: str | None,
    ) -> Avaliacao:
        neg = await self.negociacoes.get(negociacao_id)
        if neg is None:
            raise NotFoundError("Negociação não encontrada")
        if neg.status != NegociacaoStatus.CONCLUIDA:
            raise ConflictError("Avaliação só permitida após conclusão")

        # Janela de 14 dias após conclusão (combinada_em é melhor proxy se concluída automática)
        ref = neg.combinada_em or neg.updated_at
        if ref and ref + timedelta(days=JANELA_AVALIACAO_DIAS) < datetime.now(tz=timezone.utc):
            raise ConflictError("Janela de avaliação encerrada (14 dias)")

        if avaliador_conta_id not in (neg.conta_vendedora_id, neg.conta_compradora_id):
            raise ForbiddenError("Conta não participou da Negociação")
        avaliado_id = (
            neg.conta_compradora_id
            if avaliador_conta_id == neg.conta_vendedora_id
            else neg.conta_vendedora_id
        )

        if await self.vinculos.existe_entre(avaliador_conta_id, avaliado_id):
            raise VinculoDetectadoError("Avaliação recíproca bloqueada — vínculo detectado")

        existente = await self.avaliacoes.get_de_avaliador_na_negociacao(
            negociacao_id=negociacao_id, avaliador_conta_id=avaliador_conta_id
        )
        if existente:
            raise ConflictError("Avaliação já registrada para esta Negociação")

        av = Avaliacao(
            negociacao_id=negociacao_id,
            avaliador_conta_id=avaliador_conta_id,
            avaliado_conta_id=avaliado_id,
            papel_avaliado=papel_avaliado,
            nota=nota,
            subnotas=subnotas,
            comentario=comentario,
            visivel=False,
        )
        self.db.add(av)
        await self.db.flush()

        # Reciprocidade: se a contraparte já tinha avaliado, ambas viram visíveis
        recip = await self.avaliacoes.get_de_avaliador_na_negociacao(
            negociacao_id=negociacao_id, avaliador_conta_id=avaliado_id
        )
        if recip:
            av.visivel = True
            recip.visivel = True
            await self.db.flush()
        return av

    async def reputacao_por_papel(self, conta_id: UUID) -> list[dict]:
        rows = await self.db.execute(
            select(
                Avaliacao.papel_avaliado,
                func.avg(Avaliacao.nota),
                func.count(Avaliacao.id),
            )
            .where(
                Avaliacao.avaliado_conta_id == conta_id,
                Avaliacao.visivel.is_(True),
                Avaliacao.removida.is_(False),
            )
            .group_by(Avaliacao.papel_avaliado)
        )
        return [
            {"papel": r[0].value if hasattr(r[0], "value") else r[0],
             "media": float(r[1] or 0),
             "total_avaliacoes": int(r[2] or 0)}
            for r in rows
        ]


__all__ = ["ReputacaoService"]
