"""Marketplace — criação de AnuncioVenda e OfertaCompra com regras de validação,
offset de localização, limite de Plano, regulação documental (Subcategoria Regulada).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
    CondicaoForma,
    CondicaoLimpeza,
    CondicaoUmidade,
    FrequenciaAnuncio,
    OfertaCompraStatus,
)
from app.models.oferta_compra import OfertaCompra
from app.models.tipo_material import TipoMaterial
from app.repositories.assinatura import AssinaturaRepository, PlanoRepository
from app.repositories.catalogo import TipoMaterialRepository
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
        self.tipos_material = TipoMaterialRepository(db)
        self.papeis = PapelRepository(db)
        self.assinaturas = AssinaturaRepository(db)
        self.planos = PlanoRepository(db)
        self.documentos = DocumentoService(db)

    async def _carregar_tipo_com_subcategoria(self, tipo_material_id: UUID) -> TipoMaterial | None:
        from sqlalchemy import select

        return await self.db.scalar(
            select(TipoMaterial)
            .options(selectinload(TipoMaterial.subcategoria))
            .where(TipoMaterial.id == tipo_material_id)
        )

    # === AnuncioVenda ===

    async def criar_anuncio_venda(
        self,
        *,
        conta_id: UUID,
        papel_id: UUID,
        tipo_material_id: UUID,
        atributos: dict,
        condicao_limpeza: CondicaoLimpeza | None,
        condicao_umidade: CondicaoUmidade | None,
        condicao_forma: CondicaoForma | None,
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
        tipo = await self._carregar_tipo_com_subcategoria(tipo_material_id)
        if tipo is None or not tipo.ativo:
            raise NotFoundError("Tipo de Material não encontrado ou inativo")
        sub = tipo.subcategoria
        if sub is None or not sub.ativo:
            raise NotFoundError("Subcategoria do material inativa")

        papel = await self.papeis.get(papel_id)
        if papel is None or papel.conta_id != conta_id:
            raise ForbiddenError("Papel não pertence à Conta ativa")

        # Regulação documental vive na Subcategoria intermediária
        if sub.requer_validacao_documental:
            faltando = await self.documentos.documentos_faltantes_para_subcategoria(
                conta_id, sub.documentos_exigidos
            )
            if faltando:
                raise DocumentoFaltandoError(
                    "Documentos faltantes para publicar nesta Subcategoria",
                    details={"documentos_faltantes": faltando},
                )

        if frequencia == FrequenciaAnuncio.RECORRENTE and not intervalo_geracao:
            raise ValidationDomainError("Intervalo de geração obrigatório para recorrente")

        if fotos and len(fotos) > 3:
            raise ValidationDomainError("Máximo de 3 fotos por anúncio")

        await self._validar_limite_plano(conta_id=conta_id, papel_id=papel_id)

        lat_pub, lng_pub, offset_m = aplicar_offset_privacidade(
            lat_real, lng_real, territorio=territorio  # type: ignore[arg-type]
        )

        anuncio = AnuncioVenda(
            conta_id=conta_id,
            papel_id=papel_id,
            tipo_material_id=tipo_material_id,
            atributos=atributos,
            condicao_limpeza=condicao_limpeza,
            condicao_umidade=condicao_umidade,
            condicao_forma=condicao_forma,
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
        novo = AnuncioVenda(
            conta_id=anuncio.conta_id,
            papel_id=anuncio.papel_id,
            tipo_material_id=anuncio.tipo_material_id,
            atributos=dict(anuncio.atributos or {}),
            condicao_limpeza=anuncio.condicao_limpeza,
            condicao_umidade=anuncio.condicao_umidade,
            condicao_forma=anuncio.condicao_forma,
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
        tipo_material_id: UUID,
        titulo: str,
        descricao: str | None,
        especificacao: dict,
        preco_paga: Decimal,
        unidade: str,
        volume_min: Decimal,
        volume_max: Decimal | None,
        volume_minimo_kg: float | None,
        condicao_limpeza: CondicaoLimpeza | None,
        condicao_umidade: CondicaoUmidade | None,
        condicao_forma: CondicaoForma | None,
        lat: float,
        lng: float,
        raio_km: int,
        retira: bool,
        prazo_validade: datetime,
    ) -> OfertaCompra:
        tipo = await self.tipos_material.get(tipo_material_id)
        if tipo is None or not tipo.ativo:
            raise NotFoundError("Tipo de Material não encontrado ou inativo")

        papel = await self.papeis.get(papel_id)
        if papel is None or papel.conta_id != conta_id:
            raise ForbiddenError("Papel não pertence à Conta ativa")

        await self._validar_limite_plano(conta_id=conta_id, papel_id=papel_id, oferta=True)

        oferta = OfertaCompra(
            conta_id=conta_id,
            papel_id=papel_id,
            tipo_material_id=tipo_material_id,
            titulo=titulo,
            descricao=descricao,
            especificacao=especificacao,
            preco_paga=preco_paga,
            unidade=unidade,
            volume_min=volume_min,
            volume_max=volume_max,
            volume_minimo_kg=volume_minimo_kg,
            condicao_limpeza=condicao_limpeza,
            condicao_umidade=condicao_umidade,
            condicao_forma=condicao_forma,
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
        papel = await self.papeis.get(papel_id)
        if papel is None:
            raise ForbiddenError("Papel inexistente")

        if assinatura is None:
            plano = await self.planos.gratuito_por_papel(papel.papel)
        else:
            plano = await self.planos.get(assinatura.plano_id)

        if plano is None:
            return

        from sqlalchemy import func, select

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
        if total > plano.limite_publicacoes_ativas:
            raise LimitePublicacoesAtingidoError(
                "Limite de publicações ativas do Plano atingido",
                details={
                    "plano": plano.nome,
                    "limite": plano.limite_publicacoes_ativas,
                    "ativos": total,
                },
            )

    @staticmethod
    def pode_ver_localizacao_exata(anuncio: AnuncioVenda, *, aceite_bilateral: bool, status_negociacao: str) -> bool:
        return aceite_bilateral and status_negociacao in ("combinada", "concluida")


__all__ = ["MarketplaceService"]
