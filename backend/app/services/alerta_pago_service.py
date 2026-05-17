"""Alerta Pago — boost embutido na OfertaCompra com cobertura mínima e reembolso automático."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    ConflictError,
    CoberturaInsuficienteError,
    NotFoundError,
)
from app.models.anuncio_venda import AnuncioVenda
from app.models.enums import AnuncioVendaStatus
from app.models.oferta_compra import OfertaCompra
from app.models.preferencia_comunicacao import PreferenciaComunicacao
from app.repositories.conteudo import DispositivoRepository
from app.repositories.marketplace import OfertaCompraRepository
from app.services.creditos_service import CreditosService
from app.utils.geo import st_dwithin_geography
from app.utils.notifications import enviar_push


# Custo do disparo em Créditos (configurável aqui — alternativamente vir do PacoteCredito).
CUSTO_DISPARO = 10


class AlertaPagoService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.ofertas = OfertaCompraRepository(db)
        self.dispositivos = DispositivoRepository(db)
        self.creditos = CreditosService(db)

    async def ativar(
        self,
        *,
        oferta_id: UUID,
        raio_km: int,
        duracao_horas: int,
        segmentacao: dict,
    ) -> dict:
        oferta = await self.ofertas.get(oferta_id)
        if oferta is None:
            raise NotFoundError("Oferta não encontrada")
        if oferta.boost_ativo:
            raise ConflictError("Boost já está ativo nesta Oferta")

        # 1. Calcular cobertura
        cobertura, contas_alvo = await self._calcular_cobertura(
            oferta=oferta, raio_km=raio_km, segmentacao=segmentacao
        )
        cobertura_minima = settings.ALERTA_PAGO_COBERTURA_MINIMA

        # 2. Debitar créditos antes — se < cobertura mínima, reembolsa em seguida
        await self.creditos.debitar(
            conta_id=oferta.conta_id,
            valor=CUSTO_DISPARO,
            descricao=f"Alerta Pago para oferta {oferta_id}",
            referencia_tipo="oferta_compra",
            referencia_id=oferta_id,
        )

        if cobertura < cobertura_minima:
            # Reembolso integral
            await self.creditos.reembolsar(
                conta_id=oferta.conta_id,
                valor=CUSTO_DISPARO,
                descricao=f"Reembolso por cobertura insuficiente ({cobertura} < {cobertura_minima})",
                referencia_tipo="oferta_compra",
                referencia_id=oferta_id,
            )
            oferta.boost_auditoria = {
                "cobertura": cobertura,
                "cobertura_minima": cobertura_minima,
                "disparou": False,
                "creditos_debitados": CUSTO_DISPARO,
                "creditos_reembolsados": CUSTO_DISPARO,
                "ts": datetime.now(tz=timezone.utc).isoformat(),
            }
            await self.db.flush()
            return {
                "cobertura": cobertura,
                "cobertura_minima": cobertura_minima,
                "disparou": False,
                "creditos_debitados": CUSTO_DISPARO,
                "creditos_reembolsados": CUSTO_DISPARO,
                "oferta_id": oferta_id,
            }

        # 3. Ativa boost e dispara push
        now = datetime.now(tz=timezone.utc)
        oferta.boost_ativo = True
        oferta.boost_raio_km = raio_km
        oferta.boost_duracao_horas = duracao_horas
        oferta.boost_inicio = now
        oferta.boost_fim = now + timedelta(hours=duracao_horas)
        oferta.boost_segmentacao = segmentacao

        tokens: list[str] = []
        for conta_id in contas_alvo:
            tokens.extend(await self.dispositivos.tokens_ativos_de_conta(conta_id))

        resultado_push = enviar_push(
            tokens=tokens,
            titulo=f"Nova demanda: {oferta.titulo}",
            corpo=f"R$ {oferta.preco_paga}/{oferta.unidade} em até {raio_km}km",
            data={"oferta_id": str(oferta_id), "tipo": "alerta_pago"},
        )
        oferta.boost_auditoria = {
            "cobertura": cobertura,
            "cobertura_minima": cobertura_minima,
            "disparou": True,
            "creditos_debitados": CUSTO_DISPARO,
            "creditos_reembolsados": 0,
            "push": resultado_push,
            "ts": now.isoformat(),
        }
        await self.db.flush()
        return {
            "cobertura": cobertura,
            "cobertura_minima": cobertura_minima,
            "disparou": True,
            "creditos_debitados": CUSTO_DISPARO,
            "creditos_reembolsados": 0,
            "oferta_id": oferta_id,
        }

    async def _calcular_cobertura(
        self,
        *,
        oferta: OfertaCompra,
        raio_km: int,
        segmentacao: dict,
    ) -> tuple[int, list[UUID]]:
        """Conta vendedores ELEGÍVEIS no raio do boost.

        Elegível = Conta:
          - com AnuncioVenda PUBLICADO na Subcategoria da OfertaCompra
          - dentro do raio_km
          - com PreferenciaComunicacao.aceita_alerta_pago_de_terceiros=True
        """
        stmt = (
            select(AnuncioVenda.conta_id)
            .join(
                PreferenciaComunicacao,
                PreferenciaComunicacao.conta_id == AnuncioVenda.conta_id,
            )
            .where(
                AnuncioVenda.status == AnuncioVendaStatus.PUBLICADO,
                AnuncioVenda.subcategoria_id == oferta.subcategoria_id,
                PreferenciaComunicacao.aceita_alerta_pago_de_terceiros.is_(True),
                st_dwithin_geography(AnuncioVenda.geom_pub, oferta.lat, oferta.lng, raio_km),
            )
            .distinct()
        )
        contas = list(await self.db.scalars(stmt))
        # Aplicação adicional de segmentação (papéis, frequência, etc.) — fora do MVP
        _ = segmentacao
        return len(contas), contas


__all__ = ["AlertaPagoService", "CUSTO_DISPARO"]
_ = func  # mantém import vivo
