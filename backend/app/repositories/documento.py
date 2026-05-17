"""Repositórios — TipoDocumento, Documento."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select, update

from app.models.documento import Documento
from app.models.enums import DocumentoStatus
from app.models.tipo_documento import TipoDocumento
from app.repositories.base import BaseRepository


class TipoDocumentoRepository(BaseRepository[TipoDocumento]):
    model = TipoDocumento

    async def listar_para_papel(self, papel_slug: str) -> list[TipoDocumento]:
        # JSONB contains
        from sqlalchemy.dialects.postgresql import JSONB
        from sqlalchemy import cast, literal

        stmt = select(TipoDocumento).where(TipoDocumento.ativo.is_(True))
        return [
            t
            for t in await self.db.scalars(stmt)
            if not t.papeis_aplicaveis or papel_slug in t.papeis_aplicaveis
        ]

    async def get_by_slug(self, slug: str) -> TipoDocumento | None:
        return await self.db.scalar(select(TipoDocumento).where(TipoDocumento.slug == slug))


class DocumentoRepository(BaseRepository[Documento]):
    model = Documento

    async def listar_da_conta(self, conta_id: UUID) -> list[Documento]:
        return list(
            await self.db.scalars(
                select(Documento).where(Documento.conta_id == conta_id)
            )
        )

    async def get_aprovado_da_conta_por_tipo(
        self, conta_id: UUID, tipo_documento_id: UUID
    ) -> Documento | None:
        return await self.db.scalar(
            select(Documento).where(
                Documento.conta_id == conta_id,
                Documento.tipo_documento_id == tipo_documento_id,
                Documento.status == DocumentoStatus.APROVADO,
            )
        )

    async def listar_fila_pendente(self) -> list[Documento]:
        return list(
            await self.db.scalars(
                select(Documento)
                .where(Documento.status == DocumentoStatus.PENDENTE)
                .order_by(Documento.created_at.asc())
            )
        )

    async def vencer_documentos(self, *, hoje: date) -> int:
        stmt = (
            update(Documento)
            .where(
                Documento.status == DocumentoStatus.APROVADO,
                Documento.data_vencimento.is_not(None),
                Documento.data_vencimento < hoje,
            )
            .values(status=DocumentoStatus.VENCIDO)
            .execution_options(synchronize_session=False)
        )
        r = await self.db.execute(stmt)
        return r.rowcount or 0

    async def listar_vencendo_em(self, *, dias: int) -> list[Documento]:
        from datetime import timedelta

        alvo = date.today() + timedelta(days=dias)
        return list(
            await self.db.scalars(
                select(Documento).where(
                    Documento.status == DocumentoStatus.APROVADO,
                    Documento.data_vencimento == alvo,
                )
            )
        )
