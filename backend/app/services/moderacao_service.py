"""Moderação — decisão sobre Denúncia + ban de Conta + remoção de Publicação."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.redis_client import ban_conta
from app.models.anuncio_venda import AnuncioVenda
from app.models.conta import Conta, ContaStatus
from app.models.decisao_moderacao import DecisaoModeracao
from app.models.denuncia import Denuncia
from app.models.enums import (
    AcaoModeracao,
    AnuncioVendaStatus,
    DenunciaAlvoTipo,
    DenunciaStatus,
    NegociacaoStatus,
    OfertaCompraStatus,
)
from app.models.mensagem import Mensagem
from app.models.negociacao import Negociacao
from app.models.oferta_compra import OfertaCompra
from app.repositories.moderacao import DenunciaRepository


class ModeracaoService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.denuncias = DenunciaRepository(db)

    async def decidir(
        self,
        *,
        denuncia_id: UUID,
        admin_id: UUID,
        acao: AcaoModeracao,
        motivo: str,
    ) -> DecisaoModeracao:
        d = await self.denuncias.get(denuncia_id)
        if d is None:
            raise NotFoundError("Denúncia não encontrada")
        if d.status == DenunciaStatus.RESOLVIDA:
            raise ConflictError("Denúncia já resolvida")

        dec = DecisaoModeracao(
            denuncia_id=d.id, admin_id=admin_id, acao=acao, motivo=motivo
        )
        self.db.add(dec)

        await self._executar_acao(d, acao)
        d.status = DenunciaStatus.RESOLVIDA if acao != AcaoModeracao.ARQUIVAR else DenunciaStatus.ARQUIVADA
        await self.db.flush()
        return dec

    async def _executar_acao(self, denuncia: Denuncia, acao: AcaoModeracao) -> None:
        if acao in (AcaoModeracao.ARQUIVAR, AcaoModeracao.ADVERTIR):
            return

        if denuncia.alvo_tipo == DenunciaAlvoTipo.PUBLICACAO:
            await self._remover_publicacao(denuncia.alvo_id, acao)
        elif denuncia.alvo_tipo == DenunciaAlvoTipo.MENSAGEM:
            await self._ocultar_mensagem(denuncia.alvo_id)
        elif denuncia.alvo_tipo == DenunciaAlvoTipo.CONTA:
            await self._aplicar_em_conta(denuncia.alvo_id, acao)

    async def _remover_publicacao(self, alvo_id: UUID, acao: AcaoModeracao) -> None:
        # Tenta cada um dos tipos de publicação até encontrar
        for modelo, status_target in (
            (AnuncioVenda, AnuncioVendaStatus.ARQUIVADO),
            (OfertaCompra, OfertaCompraStatus.PAUSADA),
        ):
            obj = await self.db.get(modelo, alvo_id)
            if obj is None:
                continue
            if acao in (AcaoModeracao.REMOVER, AcaoModeracao.OCULTAR):
                obj.status = status_target
                await self.db.flush()
            return

    async def _ocultar_mensagem(self, alvo_id: UUID) -> None:
        msg = await self.db.get(Mensagem, alvo_id)
        if msg is None:
            return
        msg.conteudo = "[mensagem removida pela moderação]"
        await self.db.flush()

    async def _aplicar_em_conta(self, conta_id: UUID, acao: AcaoModeracao) -> None:
        from sqlalchemy import or_, select

        conta = await self.db.get(Conta, conta_id)
        if conta is None:
            return
        if acao == AcaoModeracao.SUSPENDER:
            conta.status = ContaStatus.SUSPENSA
        elif acao == AcaoModeracao.BANIR:
            conta.status = ContaStatus.SUSPENSA
            # Blocklist Redis (efeito ≤ 5min)
            await ban_conta(str(conta.id), ttl_seconds=60 * 60 * 24 * 365 * 5)
            # Cancela Negociações abertas com motivo plataforma
            negs = await self.db.scalars(
                select(Negociacao).where(
                    or_(
                        Negociacao.conta_vendedora_id == conta.id,
                        Negociacao.conta_compradora_id == conta.id,
                    ),
                    Negociacao.status.in_(
                        [NegociacaoStatus.ABERTA, NegociacaoStatus.COMBINADA]
                    ),
                )
            )
            for n in negs:
                n.status = NegociacaoStatus.CANCELADA
                n.motivo_cancelamento_texto = "Cancelada pela plataforma — moderação"
                n.cancelada_em = datetime.now(tz=timezone.utc)
        await self.db.flush()


__all__ = ["ModeracaoService"]
_: Any = AcaoModeracao  # silencia lint
