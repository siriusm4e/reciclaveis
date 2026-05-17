"""Assinatura — vincular Plano a Papel, renovar, ciclo de graça/pausada/cancelada."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.assinatura import Assinatura
from app.models.enums import AssinaturaStatus, FaturaStatus, PagamentoMetodo, PagamentoStatus
from app.models.fatura import Fatura
from app.models.pagamento import Pagamento
from app.repositories.assinatura import (
    AssinaturaRepository,
    FaturaRepository,
    PagamentoRepository,
    PlanoRepository,
)


class AssinaturaService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.assinaturas = AssinaturaRepository(db)
        self.planos = PlanoRepository(db)
        self.faturas = FaturaRepository(db)
        self.pagamentos = PagamentoRepository(db)

    async def assinar(
        self,
        *,
        conta_id: UUID,
        papel_id: UUID,
        plano_id: UUID,
        cortesia: bool = False,
    ) -> Assinatura:
        plano = await self.planos.get(plano_id)
        if plano is None or not plano.ativo:
            raise NotFoundError("Plano indisponível")

        existing = await self.assinaturas.get_do_papel(papel_id)
        if existing and existing.status not in (AssinaturaStatus.CANCELADA,):
            raise ConflictError("Papel já possui Assinatura ativa")

        now = datetime.now(tz=timezone.utc)
        ass = Assinatura(
            conta_id=conta_id,
            papel_id=papel_id,
            plano_id=plano_id,
            status=AssinaturaStatus.ATIVA,
            data_inicio=now,
            data_renovacao=now + timedelta(days=30),
            ciclo_cortesia=cortesia,
        )
        self.db.add(ass)
        await self.db.flush()

        if not plano.gratuito and not cortesia:
            await self._gerar_fatura(ass)
        return ass

    async def cancelar(self, assinatura: Assinatura) -> Assinatura:
        if assinatura.status == AssinaturaStatus.CANCELADA:
            return assinatura
        assinatura.status = AssinaturaStatus.CANCELADA
        assinatura.cancelada_em = datetime.now(tz=timezone.utc)
        await self.db.flush()
        return assinatura

    async def aplicar_cortesia(self, assinatura: Assinatura) -> Assinatura:
        """Bypass de cobrança para o ciclo atual — chamado por admin com auditoria."""
        assinatura.ciclo_cortesia = True
        if assinatura.status in (AssinaturaStatus.EM_GRACA, AssinaturaStatus.PAUSADA):
            assinatura.status = AssinaturaStatus.ATIVA
            assinatura.em_graca_desde = None
            assinatura.pausada_desde = None
        await self.db.flush()
        return assinatura

    # === Ciclo de cobrança ===

    async def gerar_renovacao(self, assinatura: Assinatura) -> Fatura | None:
        plano = await self.planos.get(assinatura.plano_id)
        if not plano or plano.gratuito:
            assinatura.data_renovacao = datetime.now(tz=timezone.utc) + timedelta(days=30)
            await self.db.flush()
            return None
        return await self._gerar_fatura(assinatura)

    async def _gerar_fatura(self, assinatura: Assinatura) -> Fatura:
        plano = await self.planos.get(assinatura.plano_id)
        if plano is None:
            raise NotFoundError("Plano não encontrado")
        agora = datetime.now(tz=timezone.utc)
        fatura = Fatura(
            assinatura_id=assinatura.id,
            ciclo_inicio=agora,
            ciclo_fim=agora + timedelta(days=30),
            valor_centavos=plano.preco_mensal_centavos,
            status=(
                FaturaStatus.CORTESIA if assinatura.ciclo_cortesia else FaturaStatus.PENDENTE
            ),
            vencimento=agora + timedelta(days=5),
        )
        self.db.add(fatura)
        await self.db.flush()
        return fatura

    async def registrar_pagamento(
        self,
        *,
        fatura: Fatura,
        valor_centavos: int,
        metodo: PagamentoMetodo,
        status: PagamentoStatus,
        gateway_id: str | None = None,
        mensagem: str | None = None,
    ) -> Pagamento:
        ultima = await self.pagamentos.ultima_tentativa(fatura.id)
        tentativa = (ultima.tentativa + 1) if ultima else 1
        p = Pagamento(
            fatura_id=fatura.id,
            valor_centavos=valor_centavos,
            metodo=metodo,
            status=status,
            tentativa=tentativa,
            gateway_id=gateway_id,
            mensagem_gateway=mensagem,
        )
        self.db.add(p)
        if status == PagamentoStatus.APROVADO:
            fatura.status = FaturaStatus.PAGA
        elif status == PagamentoStatus.FALHA:
            fatura.status = FaturaStatus.FALHA
        await self.db.flush()
        return p

    async def marcar_em_graca(self, assinatura: Assinatura) -> Assinatura:
        if assinatura.status == AssinaturaStatus.ATIVA:
            assinatura.status = AssinaturaStatus.EM_GRACA
            assinatura.em_graca_desde = datetime.now(tz=timezone.utc)
            await self.db.flush()
        return assinatura


__all__ = ["AssinaturaService"]
