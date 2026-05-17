"""Institucional — Pedido de Coleta Pública (roteamento Prefeitura) + Campanhas + Mapa."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.anuncio_venda import AnuncioVenda
from app.models.campanha_publica import CampanhaPublica
from app.models.conta import Conta, ContaTipo
from app.models.enums import (
    AnuncioVendaStatus,
    CampanhaStatus,
    PapelTipo,
    PedidoColetaStatus,
)
from app.models.papel import PapelAtivado
from app.models.pedido_coleta_publica import PedidoColetaPublica
from app.repositories.conta import ContaRepository, PapelRepository
from app.repositories.institucional import CampanhaRepository, PedidoColetaRepository
from app.utils.geo import make_point_wkt


class InstitucionalService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.pedidos = PedidoColetaRepository(db)
        self.campanhas = CampanhaRepository(db)
        self.contas = ContaRepository(db)
        self.papeis = PapelRepository(db)

    # === Pedido Coleta ===

    async def criar_pedido(
        self,
        *,
        conta_solicitante_id: UUID,
        bairro: str,
        cidade: str,
        uf: str,
        ibge: str | None,
        tipo_residuo: str,
        foto_path: str | None,
        quantidade: Decimal | None,
        descricao: str | None,
        lat: float,
        lng: float,
    ) -> PedidoColetaPublica:
        prefeitura_id = await self._resolver_prefeitura(ibge=ibge, uf=uf)
        status = (
            PedidoColetaStatus.ABERTA if prefeitura_id else PedidoColetaStatus.AGUARDANDO_MUNICIPIO
        )
        p = PedidoColetaPublica(
            conta_solicitante_id=conta_solicitante_id,
            prefeitura_conta_id=prefeitura_id,
            bairro=bairro,
            cidade=cidade,
            uf=uf,
            ibge_municipio=ibge,
            tipo_residuo=tipo_residuo,
            foto_path=foto_path,
            quantidade_estimada=quantidade,
            descricao=descricao,
            lat=lat,
            lng=lng,
            geom=make_point_wkt(lat, lng),
            status=status,
        )
        self.db.add(p)
        await self.db.flush()
        return p

    async def atualizar_status(
        self,
        *,
        pedido: PedidoColetaPublica,
        novo: PedidoColetaStatus,
        prefeitura_conta_id: UUID,
    ) -> PedidoColetaPublica:
        if pedido.prefeitura_conta_id != prefeitura_conta_id:
            raise ForbiddenError("Apenas a Prefeitura responsável pode avançar o status")
        pedido.status = novo
        await self.db.flush()
        return pedido

    async def contestar_fechamento(
        self,
        *,
        pedido: PedidoColetaPublica,
        conta_id: UUID,
    ) -> PedidoColetaPublica:
        if pedido.conta_solicitante_id != conta_id:
            raise ForbiddenError("Apenas o solicitante pode contestar")
        if pedido.status != PedidoColetaStatus.FECHADA:
            raise ConflictError("Pedido não está fechado")
        # Janela de 7 dias após fechamento
        limite = (pedido.updated_at or datetime.now(tz=timezone.utc)) + timedelta(days=7)
        if datetime.now(tz=timezone.utc) > limite:
            raise ConflictError("Janela de contestação encerrada (7 dias)")
        pedido.status = PedidoColetaStatus.CONTESTADA
        await self.db.flush()
        return pedido

    async def _resolver_prefeitura(self, *, ibge: str | None, uf: str) -> UUID | None:
        if not ibge:
            return None
        # Conta Órgão Público com escopo_territorial casando IBGE/UF e Papel PREFEITURA ativo
        stmt = (
            select(Conta.id)
            .join(PapelAtivado, PapelAtivado.conta_id == Conta.id)
            .where(
                Conta.tipo == ContaTipo.ORGAO_PUBLICO,
                PapelAtivado.papel == PapelTipo.PREFEITURA,
                Conta.escopo_territorial["ibge"].astext == ibge,
            )
        )
        return await self.db.scalar(stmt)

    # === Campanhas ===

    async def criar_campanha(self, **kw) -> CampanhaPublica:
        c = CampanhaPublica(**kw)
        self.db.add(c)
        await self.db.flush()
        return c

    async def atualizar_campanha(self, c: CampanhaPublica, **kw) -> CampanhaPublica:
        for k, v in kw.items():
            if v is not None and hasattr(c, k):
                setattr(c, k, v)
        await self.db.flush()
        return c

    # === Mapa institucional (agregado por município) ===

    async def mapa_municipio(self, ibge: str) -> list[dict]:
        # Contagens agregadas para o município (uma célula por bairro reportado)
        rows = await self.db.execute(
            select(
                PedidoColetaPublica.bairro,
                func.count(PedidoColetaPublica.id),
            )
            .where(
                PedidoColetaPublica.ibge_municipio == ibge,
                PedidoColetaPublica.status.in_(
                    [
                        PedidoColetaStatus.ABERTA,
                        PedidoColetaStatus.TRIADA,
                        PedidoColetaStatus.AGENDADA,
                    ]
                ),
            )
            .group_by(PedidoColetaPublica.bairro)
        )
        celulas: list[dict] = []
        for bairro, total in rows:
            anuncios = int(
                await self.db.scalar(
                    select(func.count())
                    .select_from(AnuncioVenda)
                    .where(AnuncioVenda.status == AnuncioVendaStatus.PUBLICADO)
                )
                or 0
            )
            campanhas = int(
                await self.db.scalar(
                    select(func.count())
                    .select_from(CampanhaPublica)
                    .where(
                        CampanhaPublica.ibge_municipio == ibge,
                        CampanhaPublica.status == CampanhaStatus.PUBLICADA,
                    )
                )
                or 0
            )
            celulas.append(
                {
                    "bairro": bairro,
                    "ibge_municipio": ibge,
                    "pedidos_abertos": int(total),
                    "anuncios_ativos": anuncios,
                    "campanhas_ativas": campanhas,
                }
            )
        return celulas

    async def valida_acesso_mapa(
        self, *, conta: Conta, ibge: str | None = None, uf: str | None = None
    ) -> None:
        if conta.tipo != ContaTipo.ORGAO_PUBLICO:
            raise ForbiddenError("Mapa institucional restrito a Órgão Público")
        escopo = conta.escopo_territorial or {}
        if ibge and escopo.get("ibge") != ibge:
            raise ForbiddenError("Mapa restrito ao próprio município")
        if uf and escopo.get("uf") != uf:
            raise ForbiddenError("Mapa restrito ao próprio estado")


__all__ = ["InstitucionalService"]
_ = NotFoundError  # mantém import vivo
