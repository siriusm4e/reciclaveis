"""Marketplace — criação de AnuncioVenda e OfertaCompra com regras de validação,
offset de localização, limite de Plano, Subcategoria Regulada.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DocumentoFaltandoError,
    ForbiddenError,
    LimitePublicacoesAtingidoError,
    NotFoundError,
    ValidationDomainError,
)
from app.models.anuncio_venda import AnuncioVenda
from app.models.enums import (
    AnuncioVendaStatus,
    FrequenciaAnuncio,
    OfertaCompraStatus,
    PapelTipo,
)
from app.models.oferta_compra import OfertaCompra
from app.repositories.assinatura import AssinaturaRepository, PlanoRepository
from app.repositories.catalogo import SubcategoriaRepository
from app.repositories.marketplace import (
    AnuncioVendaRepository,
    OfertaCompraRepository,
)
from app.repositories.conta import PapelRepository
from app.services.documento_service import DocumentoService
from app.utils.geo import aplicar_offset_privacidade, make_point_wkt


class MarketplaceService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.anuncios = AnuncioVendaRepository(db)
        self.ofertas = OfertaCompraRepository(db)
        self.subcategorias = SubcategoriaRepository(db)
        self.papeis = PapelRepository(db)
        self.assinaturas = AssinaturaRepository(db)
        self.planos = PlanoRepository(db)
        self.documentos = DocumentoService(db)

    # === AnuncioVenda ===

    async def criar_anuncio_venda(
        self,
        *,
        conta_id: UUID,
        papel_id: UUID,
        subcategoria_id: UUID,
        titulo: str,
        descricao: str | None,
        atributos: dict,
        lat_real: float,
        lng_real: float,
        territorio: str,
        preco_pretendido: Decimal,
        unidade: str,
        volume_estimado: Decimal | None,
        frequencia: FrequenciaAnuncio,
        intervalo_geracao: str | None,
        prazo_validade: datetime,
        fotos: list[str],
        aceita_alerta_pago_de_terceiros: bool = True,
    ) -> AnuncioVenda:
        sub = await self.subcategorias.get(subcategoria_id)
        if sub is None or not sub.ativo:
            raise NotFoundError("Subcategoria não encontrada ou inativa")

        papel = await self.papeis.get(papel_id)
        if papel is None or papel.conta_id != conta_id:
            raise ForbiddenError("Papel não pertence à Conta ativa")

        # Subcategoria Regulada → exige Documento aprovado
        if sub.requer_validacao_documental:
            faltando = await self.documentos.documentos_faltantes_para_subcategoria(
                conta_id, sub.documentos_exigidos
            )
            if faltando:
                raise DocumentoFaltandoError(
                    "Documentos faltantes para publicar nesta Subcategoria",
                    details={"documentos_faltantes": faltando},
                )

        # Frequência recorrente exige intervalo_geracao
        if frequencia == FrequenciaAnuncio.RECORRENTE and not intervalo_geracao:
            raise ValidationDomainError("Intervalo de geração obrigatório para recorrente")

        # Limite do Plano (publicações ativas)
        await self._validar_limite_plano(conta_id=conta_id, papel_id=papel_id)

        # Offset de privacidade (calculado UMA VEZ aqui)
        lat_pub, lng_pub, offset_m = aplicar_offset_privacidade(
            lat_real, lng_real, territorio=territorio  # type: ignore[arg-type]
        )

        anuncio = AnuncioVenda(
            conta_id=conta_id,
            papel_id=papel_id,
            subcategoria_id=subcategoria_id,
            titulo=titulo,
            descricao=descricao,
            atributos=atributos,
            lat_real=lat_real,
            lng_real=lng_real,
            lat_pub=lat_pub,
            lng_pub=lng_pub,
            offset_m=offset_m,
            geom_pub=make_point_wkt(lat_pub, lng_pub),
            territorio=territorio,
            preco_pretendido=preco_pretendido,
            unidade=unidade,
            volume_estimado=volume_estimado,
            frequencia=frequencia,
            intervalo_geracao=intervalo_geracao,
            prazo_validade=prazo_validade,
            status=AnuncioVendaStatus.PUBLICADO,
            fotos=fotos,
            aceita_alerta_pago_de_terceiros=aceita_alerta_pago_de_terceiros,
        )
        self.db.add(anuncio)
        await self.db.flush()
        return anuncio

    async def atualizar_anuncio(self, anuncio: AnuncioVenda, **kw) -> AnuncioVenda:
        for k, v in kw.items():
            if v is not None and hasattr(anuncio, k):
                setattr(anuncio, k, v)
        await self.db.flush()
        return anuncio

    async def replicar_anuncio(self, anuncio: AnuncioVenda) -> AnuncioVenda:
        """Cria uma cópia em rascunho — mantém atributos, recalcula offset ao publicar."""
        novo = AnuncioVenda(
            conta_id=anuncio.conta_id,
            papel_id=anuncio.papel_id,
            subcategoria_id=anuncio.subcategoria_id,
            titulo=f"{anuncio.titulo} (cópia)",
            descricao=anuncio.descricao,
            atributos=dict(anuncio.atributos or {}),
            lat_real=anuncio.lat_real,
            lng_real=anuncio.lng_real,
            lat_pub=anuncio.lat_pub,
            lng_pub=anuncio.lng_pub,
            offset_m=anuncio.offset_m,
            geom_pub=make_point_wkt(anuncio.lat_pub, anuncio.lng_pub),
            territorio=anuncio.territorio,
            preco_pretendido=anuncio.preco_pretendido,
            unidade=anuncio.unidade,
            volume_estimado=anuncio.volume_estimado,
            frequencia=anuncio.frequencia,
            intervalo_geracao=anuncio.intervalo_geracao,
            prazo_validade=anuncio.prazo_validade,
            status=AnuncioVendaStatus.RASCUNHO,
            fotos=list(anuncio.fotos or []),
            aceita_alerta_pago_de_terceiros=anuncio.aceita_alerta_pago_de_terceiros,
        )
        self.db.add(novo)
        await self.db.flush()
        return novo

    async def incrementar_visualizacao(self, anuncio: AnuncioVenda) -> None:
        anuncio.visualizacoes += 1
        await self.db.flush()

    # === OfertaCompra ===

    async def criar_oferta_compra(
        self,
        *,
        conta_id: UUID,
        papel_id: UUID,
        subcategoria_id: UUID,
        titulo: str,
        descricao: str | None,
        especificacao: dict,
        preco_paga: Decimal,
        unidade: str,
        volume_min: Decimal,
        volume_max: Decimal | None,
        lat: float,
        lng: float,
        raio_km: int,
        retira: bool,
        prazo_validade: datetime,
    ) -> OfertaCompra:
        sub = await self.subcategorias.get(subcategoria_id)
        if sub is None or not sub.ativo:
            raise NotFoundError("Subcategoria não encontrada ou inativa")

        papel = await self.papeis.get(papel_id)
        if papel is None or papel.conta_id != conta_id:
            raise ForbiddenError("Papel não pertence à Conta ativa")

        # Limite do Plano
        await self._validar_limite_plano(conta_id=conta_id, papel_id=papel_id, oferta=True)

        oferta = OfertaCompra(
            conta_id=conta_id,
            papel_id=papel_id,
            subcategoria_id=subcategoria_id,
            titulo=titulo,
            descricao=descricao,
            especificacao=especificacao,
            preco_paga=preco_paga,
            unidade=unidade,
            volume_min=volume_min,
            volume_max=volume_max,
            lat=lat,
            lng=lng,
            raio_km=raio_km,
            geom=make_point_wkt(lat, lng),
            retira=retira,
            prazo_validade=prazo_validade,
            status=OfertaCompraStatus.PUBLICADA,
        )
        self.db.add(oferta)
        await self.db.flush()
        return oferta

    # === Util — limite de publicações do Plano ===

    async def _validar_limite_plano(
        self, *, conta_id: UUID, papel_id: UUID, oferta: bool = False
    ) -> None:
        assinatura = await self.assinaturas.get_do_papel(papel_id)
        # Sem assinatura: usa plano gratuito do Papel (se existir)
        papel = await self.papeis.get(papel_id)
        if papel is None:
            raise ForbiddenError("Papel inexistente")

        if assinatura is None:
            plano = await self.planos.gratuito_por_papel(papel.papel)
        else:
            plano = await self.planos.get(assinatura.plano_id)

        if plano is None:
            return  # sem limite definido — política aberta

        # Conta ativas (anuncios + ofertas combinadas)
        from sqlalchemy import func, or_, select

        ativos_anuncios = int(
            await self.db.scalar(
                select(func.count())
                .select_from(AnuncioVenda)
                .where(
                    AnuncioVenda.conta_id == conta_id,
                    AnuncioVenda.papel_id == papel_id,
                    AnuncioVenda.status == AnuncioVendaStatus.PUBLICADO,
                )
            )
            or 0
        )
        ativos_ofertas = int(
            await self.db.scalar(
                select(func.count())
                .select_from(OfertaCompra)
                .where(
                    OfertaCompra.conta_id == conta_id,
                    OfertaCompra.papel_id == papel_id,
                    OfertaCompra.status == OfertaCompraStatus.PUBLICADA,
                )
            )
            or 0
        )
        total = ativos_anuncios + ativos_ofertas + (1 if not oferta else 0)
        # +1 porque vamos publicar mais uma agora (anúncio)
        if total > plano.limite_publicacoes_ativas:
            raise LimitePublicacoesAtingidoError(
                "Limite de publicações ativas do Plano atingido",
                details={
                    "plano": plano.nome,
                    "limite": plano.limite_publicacoes_ativas,
                    "ativos": total,
                },
            )

    # === Liberar localização exata (acessível por route de Negociação) ===

    @staticmethod
    def pode_ver_localizacao_exata(anuncio: AnuncioVenda, *, aceite_bilateral: bool, status_negociacao: str) -> bool:
        return aceite_bilateral and status_negociacao in ("combinada", "concluida")


__all__ = ["MarketplaceService"]
