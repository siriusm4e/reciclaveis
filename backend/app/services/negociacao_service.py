"""Negociação — abertura, mensagens, sinalização combinado, conclusão, cancelamento, disputa."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    LocalizacaoExataNaoAutorizadaError,
    NotFoundError,
    ValidationDomainError,
)
from app.models.anuncio_venda import AnuncioVenda
from app.models.enums import (
    MensagemTipo,
    MotivoCancelamento,
    NegociacaoStatus,
    PublicacaoTipo,
)
from app.models.mensagem import Mensagem
from app.models.negociacao import Negociacao
from app.models.oferta_compra import OfertaCompra
from app.repositories.marketplace import (
    AnuncioVendaRepository,
    OfertaCompraRepository,
)
from app.repositories.negociacao import MensagemRepository, NegociacaoRepository
from app.utils.sanitize import sanitize_chat
from app.utils.ws_pubsub import canal_negociacao, publicar


class NegociacaoService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.negociacoes = NegociacaoRepository(db)
        self.mensagens = MensagemRepository(db)
        self.anuncios = AnuncioVendaRepository(db)
        self.ofertas = OfertaCompraRepository(db)

    # === Abertura ===

    async def abrir(
        self,
        *,
        publicacao_id: UUID,
        publicacao_tipo: PublicacaoTipo,
        conta_iniciadora_id: UUID,
    ) -> Negociacao:
        # Determinar quem é vendedor / comprador segundo o tipo de publicação
        if publicacao_tipo == PublicacaoTipo.ANUNCIO_VENDA:
            anuncio = await self.anuncios.get(publicacao_id)
            if anuncio is None:
                raise NotFoundError("Anúncio não encontrado")
            if anuncio.conta_id == conta_iniciadora_id:
                raise ConflictError("Não é possível negociar com o próprio anúncio")
            vendedora = anuncio.conta_id
            compradora = conta_iniciadora_id
        elif publicacao_tipo == PublicacaoTipo.OFERTA_COMPRA:
            oferta = await self.ofertas.get(publicacao_id)
            if oferta is None:
                raise NotFoundError("Oferta não encontrada")
            if oferta.conta_id == conta_iniciadora_id:
                raise ConflictError("Não é possível negociar com a própria oferta")
            vendedora = conta_iniciadora_id
            compradora = oferta.conta_id
        else:
            # Para máquina/serviço/frete/oportunidade: iniciador é cliente; criador = ofertante
            vendedora_pub = await self._resolver_conta_ofertante(publicacao_id, publicacao_tipo)
            if vendedora_pub == conta_iniciadora_id:
                raise ConflictError("Não é possível negociar com a própria publicação")
            vendedora = vendedora_pub
            compradora = conta_iniciadora_id

        # Já existe uma aberta entre o mesmo par sobre a mesma publicação?
        existente = await self.negociacoes.existe_aberta(
            publicacao_id=publicacao_id,
            publicacao_tipo=publicacao_tipo,
            conta_vendedora_id=vendedora,
            conta_compradora_id=compradora,
        )
        if existente is not None:
            return existente

        neg = Negociacao(
            publicacao_id=publicacao_id,
            publicacao_tipo=publicacao_tipo,
            conta_vendedora_id=vendedora,
            conta_compradora_id=compradora,
            audit_trail=[
                {
                    "transicao": "abertura",
                    "ts": datetime.now(tz=timezone.utc).isoformat(),
                    "conta_id": str(conta_iniciadora_id),
                }
            ],
        )
        self.db.add(neg)
        await self.db.flush()
        return neg

    async def _resolver_conta_ofertante(
        self, publicacao_id: UUID, tipo: PublicacaoTipo
    ) -> UUID:
        from app.models.anuncio_frete import AnuncioFrete
        from app.models.anuncio_maquina import AnuncioMaquina
        from app.models.anuncio_servico import AnuncioServico
        from app.models.oportunidade import Oportunidade

        modelo = {
            PublicacaoTipo.ANUNCIO_MAQUINA: AnuncioMaquina,
            PublicacaoTipo.ANUNCIO_SERVICO: AnuncioServico,
            PublicacaoTipo.ANUNCIO_FRETE: AnuncioFrete,
            PublicacaoTipo.OPORTUNIDADE: Oportunidade,
        }[tipo]
        obj = await self.db.get(modelo, publicacao_id)
        if obj is None:
            raise NotFoundError("Publicação não encontrada")
        return obj.conta_id

    # === Mensagens ===

    async def enviar_mensagem(
        self,
        *,
        negociacao: Negociacao,
        conta_remetente_id: UUID,
        usuario_remetente_id: UUID | None,
        conteudo: str,
        tipo: MensagemTipo = MensagemTipo.TEXTO,
    ) -> Mensagem:
        self._valida_parte(negociacao, conta_remetente_id)
        if negociacao.status in (NegociacaoStatus.CANCELADA, NegociacaoStatus.EXPIRADA):
            raise ConflictError("Negociação em estado terminal — chat fechado")

        clean = sanitize_chat(conteudo)
        if not clean:
            raise ValidationDomainError("Mensagem vazia após sanitização")

        msg = Mensagem(
            negociacao_id=negociacao.id,
            conta_remetente_id=conta_remetente_id,
            usuario_remetente_id=usuario_remetente_id,
            conteudo=clean,
            tipo=tipo,
        )
        self.db.add(msg)
        negociacao.ultima_mensagem_em = datetime.now(tz=timezone.utc)
        negociacao.ultima_mensagem_preview = clean[:255]
        await self.db.flush()

        await publicar(
            canal_negociacao(negociacao.id),
            "nova_mensagem",
            {
                "negociacao_id": str(negociacao.id),
                "remetente_conta_id": str(conta_remetente_id),
                "conteudo": clean,
                "created_at": msg.created_at.isoformat(),
            },
        )
        return msg

    # === Sinalização "combinado" — 48h para a outra parte confirmar ===

    async def sinalizar_combinado(self, *, negociacao: Negociacao, conta_id: UUID) -> Negociacao:
        self._valida_parte(negociacao, conta_id)
        if negociacao.status != NegociacaoStatus.ABERTA:
            raise ConflictError(f"Negociação em {negociacao.status.value}")
        now = datetime.now(tz=timezone.utc)
        if conta_id == negociacao.conta_vendedora_id:
            negociacao.sinalizou_combinado_vendedor_em = now
        else:
            negociacao.sinalizou_combinado_comprador_em = now
        self._registra_audit(negociacao, "sinalizou_combinado", conta_id)
        await self.db.flush()
        return negociacao

    async def confirmar_combinado(self, *, negociacao: Negociacao, conta_id: UUID) -> Negociacao:
        self._valida_parte(negociacao, conta_id)
        if negociacao.status != NegociacaoStatus.ABERTA:
            raise ConflictError(f"Negociação em {negociacao.status.value}")

        now = datetime.now(tz=timezone.utc)
        if conta_id == negociacao.conta_vendedora_id:
            negociacao.sinalizou_combinado_vendedor_em = now
        else:
            negociacao.sinalizou_combinado_comprador_em = now

        if negociacao.sinalizou_combinado_vendedor_em and negociacao.sinalizou_combinado_comprador_em:
            negociacao.status = NegociacaoStatus.COMBINADA
            negociacao.combinada_em = now
            self._registra_audit(negociacao, "combinada", conta_id)
            await publicar(
                canal_negociacao(negociacao.id),
                "status_alterado",
                {
                    "negociacao_id": str(negociacao.id),
                    "status_anterior": "aberta",
                    "status_novo": "combinada",
                    "acionado_por": str(conta_id),
                },
            )
        await self.db.flush()
        return negociacao

    # === Localização exata bilateral ===

    async def aceitar_localizacao_exata(
        self, *, negociacao: Negociacao, conta_id: UUID
    ) -> Negociacao:
        self._valida_parte(negociacao, conta_id)
        if conta_id == negociacao.conta_vendedora_id:
            negociacao.aceite_localizacao_exata_vendedor = True
        else:
            negociacao.aceite_localizacao_exata_comprador = True
        self._registra_audit(negociacao, "aceite_localizacao_exata", conta_id)
        await self.db.flush()
        return negociacao

    async def revelar_localizacao_exata(self, negociacao: Negociacao) -> tuple[float, float]:
        if not (
            negociacao.aceite_localizacao_exata_vendedor
            and negociacao.aceite_localizacao_exata_comprador
        ):
            raise LocalizacaoExataNaoAutorizadaError("Aceite bilateral obrigatório")
        if negociacao.status not in (NegociacaoStatus.COMBINADA, NegociacaoStatus.CONCLUIDA):
            raise LocalizacaoExataNaoAutorizadaError(
                "Localização exata só após estado combinada/concluída"
            )
        if negociacao.publicacao_tipo != PublicacaoTipo.ANUNCIO_VENDA:
            raise LocalizacaoExataNaoAutorizadaError(
                "Localização exata só se aplica a AnuncioVenda"
            )
        anuncio = await self.anuncios.get(negociacao.publicacao_id)
        if anuncio is None:
            raise NotFoundError("Anúncio não encontrado")
        return anuncio.lat_real, anuncio.lng_real

    # === Conclusão, cancelamento, disputa ===

    async def concluir(self, *, negociacao: Negociacao, conta_id: UUID) -> Negociacao:
        self._valida_parte(negociacao, conta_id)
        if negociacao.status not in (NegociacaoStatus.COMBINADA, NegociacaoStatus.ABERTA):
            raise ConflictError(f"Negociação em {negociacao.status.value}")
        negociacao.status = NegociacaoStatus.CONCLUIDA
        self._registra_audit(negociacao, "concluida", conta_id)
        await self.db.flush()
        return negociacao

    async def cancelar(
        self,
        *,
        negociacao: Negociacao,
        conta_id: UUID,
        motivo: MotivoCancelamento,
        texto: str,
    ) -> Negociacao:
        self._valida_parte(negociacao, conta_id)
        if negociacao.status in (NegociacaoStatus.CONCLUIDA, NegociacaoStatus.CANCELADA):
            raise ConflictError("Negociação já finalizada")
        negociacao.status = NegociacaoStatus.CANCELADA
        negociacao.motivo_cancelamento = motivo
        negociacao.motivo_cancelamento_texto = texto
        negociacao.cancelada_por_conta_id = conta_id
        negociacao.cancelada_em = datetime.now(tz=timezone.utc)
        self._registra_audit(negociacao, "cancelada", conta_id, motivo=motivo.value)
        await self.db.flush()
        return negociacao

    async def disputar(self, *, negociacao: Negociacao, conta_id: UUID) -> Negociacao:
        self._valida_parte(negociacao, conta_id)
        if negociacao.status not in (NegociacaoStatus.COMBINADA, NegociacaoStatus.ABERTA):
            raise ConflictError(f"Negociação em {negociacao.status.value}")
        negociacao.status = NegociacaoStatus.DISPUTADA
        self._registra_audit(negociacao, "disputada", conta_id)
        await self.db.flush()
        return negociacao

    # === Helpers ===

    def _valida_parte(self, negociacao: Negociacao, conta_id: UUID) -> None:
        if conta_id not in (negociacao.conta_vendedora_id, negociacao.conta_compradora_id):
            raise ForbiddenError("Conta não participa desta Negociação")

    def _registra_audit(
        self, negociacao: Negociacao, transicao: str, conta_id: UUID, **extra: Any
    ) -> None:
        entry = {
            "transicao": transicao,
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "conta_id": str(conta_id),
            **extra,
        }
        trilha = list(negociacao.audit_trail or [])
        trilha.append(entry)
        negociacao.audit_trail = trilha


__all__ = ["NegociacaoService"]
_ = AnuncioVenda  # mantém import vivo
_ = OfertaCompra
