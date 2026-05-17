"""Documentos — upload, aprovação manual, renovação, alertas de vencimento."""

from __future__ import annotations

from datetime import date
from typing import BinaryIO
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.documento import Documento
from app.models.enums import DocumentoStatus
from app.models.tipo_documento import TipoDocumento
from app.repositories.documento import DocumentoRepository, TipoDocumentoRepository
from app.utils.upload import validar_e_salvar


class DocumentoService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.documentos = DocumentoRepository(db)
        self.tipos = TipoDocumentoRepository(db)

    async def upload(
        self,
        *,
        conta_id: UUID,
        tipo_documento_id: UUID,
        file_obj: BinaryIO,
        declared_filename: str | None,
        estabelecimento_id: UUID | None = None,
        numero: str | None = None,
        data_emissao: date | None = None,
        data_vencimento: date | None = None,
    ) -> Documento:
        tipo = await self.tipos.get(tipo_documento_id)
        if tipo is None or not tipo.ativo:
            raise NotFoundError("TipoDocumento não encontrado ou inativo")

        if tipo.tem_vencimento and not data_vencimento:
            raise ConflictError(
                "Documento exige data de vencimento",
                details={"tipo_documento_id": str(tipo_documento_id)},
            )

        path, mime, tamanho = validar_e_salvar(
            file_obj=file_obj, subpasta="documentos", declared_filename=declared_filename
        )

        # Documento anterior do mesmo tipo (para cadeia substitui_id)
        anterior = await self.documentos.get_aprovado_da_conta_por_tipo(conta_id, tipo_documento_id)

        doc = Documento(
            conta_id=conta_id,
            estabelecimento_id=estabelecimento_id,
            tipo_documento_id=tipo_documento_id,
            numero=numero,
            data_emissao=data_emissao,
            data_vencimento=data_vencimento,
            arquivo_path=path,
            mime=mime,
            tamanho_bytes=tamanho,
            status=DocumentoStatus.PENDENTE,
            substitui_id=anterior.id if anterior else None,
        )

        # Aprovação automática SOMENTE se tipo permitir e não exigir aprovação manual
        if not tipo.exige_aprovacao_manual:
            doc.status = DocumentoStatus.APROVADO

        self.db.add(doc)
        await self.db.flush()
        return doc

    async def aprovar(self, doc_id: UUID, *, admin_id: UUID) -> Documento:
        doc = await self.documentos.get(doc_id)
        if doc is None:
            raise NotFoundError("Documento não encontrado")
        if doc.status != DocumentoStatus.PENDENTE:
            raise ConflictError(f"Documento no estado {doc.status.value}")

        tipo = await self.tipos.get(doc.tipo_documento_id)
        # Regra absoluta: tipos com exige_aprovacao_manual nunca passam silenciosos
        if tipo and not tipo.exige_aprovacao_manual:
            raise ForbiddenError(
                "Tipo aceita aprovação automática — usar fluxo de upload, não /aprovar"
            )

        doc.status = DocumentoStatus.APROVADO
        doc.aprovado_por_admin_id = admin_id
        await self.db.flush()
        return doc

    async def rejeitar(self, doc_id: UUID, *, admin_id: UUID, motivo: str) -> Documento:
        doc = await self.documentos.get(doc_id)
        if doc is None:
            raise NotFoundError("Documento não encontrado")
        doc.status = DocumentoStatus.REJEITADO
        doc.aprovado_por_admin_id = admin_id
        doc.motivo_rejeicao = motivo
        await self.db.flush()
        return doc

    async def conta_tem_aprovado(self, conta_id: UUID, tipo_slug: str) -> bool:
        tipo = await self.tipos.get_by_slug(tipo_slug)
        if tipo is None:
            return False
        existe = await self.documentos.get_aprovado_da_conta_por_tipo(conta_id, tipo.id)
        return existe is not None

    async def documentos_faltantes_para_subcategoria(
        self, conta_id: UUID, docs_exigidos: list[str]
    ) -> list[str]:
        """Retorna slugs faltantes para publicar em Subcategoria Regulada."""
        faltantes: list[str] = []
        for slug in docs_exigidos:
            if not await self.conta_tem_aprovado(conta_id, slug):
                faltantes.append(slug)
        return faltantes


__all__ = ["DocumentoService"]
_ = TipoDocumento  # mantém import vivo
