"""Oportunidade — submissão de Proposta com verificação documental, declaração de vencedor."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    DocumentoFaltandoError,
    ForbiddenError,
    NotFoundError,
)
from app.models.enums import OportunidadeStatus, PropostaStatus
from app.models.oportunidade import Oportunidade
from app.models.proposta import Proposta
from app.repositories.oportunidade import OportunidadeRepository, PropostaRepository
from app.services.documento_service import DocumentoService


class OportunidadeService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.oportunidades = OportunidadeRepository(db)
        self.propostas = PropostaRepository(db)
        self.documentos = DocumentoService(db)

    async def criar(
        self,
        *,
        conta_id: UUID,
        titulo: str,
        descricao: str,
        subcategoria_id: UUID,
        tipo,  # OportunidadeTipo
        documentos_exigidos: list[str],
        prazo_submissao: datetime,
        valor_estimado: Decimal | None,
    ) -> Oportunidade:
        op = Oportunidade(
            conta_id=conta_id,
            titulo=titulo,
            descricao=descricao,
            subcategoria_id=subcategoria_id,
            tipo=tipo,
            documentos_exigidos=documentos_exigidos,
            prazo_submissao=prazo_submissao,
            valor_estimado=valor_estimado,
        )
        self.db.add(op)
        await self.db.flush()
        return op

    async def submeter_proposta(
        self,
        *,
        oportunidade_id: UUID,
        conta_proponente_id: UUID,
        valor: Decimal,
        condicoes: str | None,
        documentos_anexos: list[str],
    ) -> Proposta:
        op = await self.oportunidades.get(oportunidade_id)
        if op is None:
            raise NotFoundError("Oportunidade não encontrada")
        if op.status != OportunidadeStatus.ABERTA_PARA_PROPOSTA:
            raise ConflictError(f"Oportunidade em {op.status.value}")
        if op.prazo_submissao < datetime.now(tz=timezone.utc):
            raise ConflictError("Prazo de submissão encerrado")
        if op.conta_id == conta_proponente_id:
            raise ConflictError("Conta criadora não pode submeter Proposta")

        # Bloqueia se Documento exigido ausente
        faltando = await self.documentos.documentos_faltantes_para_subcategoria(
            conta_proponente_id, op.documentos_exigidos
        )
        if faltando:
            raise DocumentoFaltandoError(
                "Documentos exigidos pela Oportunidade estão faltando",
                details={"documentos_faltantes": faltando},
            )

        existente = await self.propostas.get_da_conta_na_oportunidade(
            conta_proponente_id, oportunidade_id
        )
        if existente:
            raise ConflictError("Já existe Proposta desta Conta para esta Oportunidade")

        p = Proposta(
            oportunidade_id=oportunidade_id,
            conta_proponente_id=conta_proponente_id,
            valor=valor,
            condicoes=condicoes,
            documentos_anexos=documentos_anexos,
            status=PropostaStatus.SUBMETIDA,
        )
        self.db.add(p)
        await self.db.flush()
        return p

    async def declarar_vencedor(
        self,
        *,
        oportunidade: Oportunidade,
        proposta_id: UUID,
    ) -> Oportunidade:
        if oportunidade.status != OportunidadeStatus.ABERTA_PARA_PROPOSTA:
            raise ConflictError("Oportunidade não está aberta")

        proposta = await self.propostas.get(proposta_id)
        if proposta is None or proposta.oportunidade_id != oportunidade.id:
            raise NotFoundError("Proposta não pertence à Oportunidade")

        proposta.status = PropostaStatus.VENCEDORA
        oportunidade.status = OportunidadeStatus.VENCEDOR_DECLARADO
        oportunidade.proposta_vencedora_id = proposta.id

        # Recusa demais
        outras = await self.propostas.listar_da_oportunidade(oportunidade.id)
        for p in outras:
            if p.id != proposta.id and p.status == PropostaStatus.SUBMETIDA:
                p.status = PropostaStatus.RECUSADA
        await self.db.flush()
        return oportunidade

    async def encerrar(self, oportunidade: Oportunidade) -> Oportunidade:
        if oportunidade.status != OportunidadeStatus.ABERTA_PARA_PROPOSTA:
            raise ConflictError("Oportunidade não está aberta")
        oportunidade.status = OportunidadeStatus.ENCERRADA
        await self.db.flush()
        return oportunidade


__all__ = ["OportunidadeService"]
_ = ForbiddenError
