"""Repositórios — Denuncia, DecisaoModeracao, PerfilInterno, AuditLog."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.models.decisao_moderacao import DecisaoModeracao
from app.models.denuncia import Denuncia
from app.models.enums import DenunciaStatus, PerfilInternoTipo
from app.models.perfil_interno import PerfilInterno, PermissaoBackoffice
from app.repositories.base import BaseRepository


class DenunciaRepository(BaseRepository[Denuncia]):
    model = Denuncia

    async def fila_aberta(self, *, limit: int = 50, offset: int = 0) -> list[Denuncia]:
        return list(
            await self.db.scalars(
                select(Denuncia)
                .where(Denuncia.status.in_([DenunciaStatus.ABERTA, DenunciaStatus.EM_ANALISE]))
                .order_by(Denuncia.created_at.asc())
                .limit(limit)
                .offset(offset)
            )
        )

    async def listar_do_denunciante(self, conta_id: UUID) -> list[Denuncia]:
        return list(
            await self.db.scalars(
                select(Denuncia).where(Denuncia.denunciante_conta_id == conta_id)
            )
        )


class DecisaoModeracaoRepository(BaseRepository[DecisaoModeracao]):
    model = DecisaoModeracao

    async def listar_da_denuncia(self, denuncia_id: UUID) -> list[DecisaoModeracao]:
        return list(
            await self.db.scalars(
                select(DecisaoModeracao)
                .where(DecisaoModeracao.denuncia_id == denuncia_id)
                .order_by(DecisaoModeracao.created_at.desc())
            )
        )


class PerfilInternoRepository(BaseRepository[PerfilInterno]):
    model = PerfilInterno

    async def get_do_usuario(self, usuario_id: UUID) -> PerfilInterno | None:
        return await self.db.scalar(
            select(PerfilInterno).where(PerfilInterno.usuario_id == usuario_id)
        )


class PermissaoBackofficeRepository(BaseRepository[PermissaoBackoffice]):
    model = PermissaoBackoffice

    async def permite(
        self, perfil: PerfilInternoTipo, recurso: str, acao: str
    ) -> bool:
        row = await self.db.scalar(
            select(PermissaoBackoffice).where(
                PermissaoBackoffice.perfil == perfil,
                PermissaoBackoffice.recurso == recurso,
                PermissaoBackoffice.acao == acao,
            )
        )
        # Default-deny se não existir entrada
        return bool(row and row.permitido)


class AuditLogRepository(BaseRepository[AuditLog]):
    model = AuditLog

    async def listar(
        self,
        *,
        recurso_tipo: str | None = None,
        recurso_id: UUID | None = None,
        admin_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        stmt = select(AuditLog)
        if recurso_tipo:
            stmt = stmt.where(AuditLog.recurso_tipo == recurso_tipo)
        if recurso_id:
            stmt = stmt.where(AuditLog.recurso_id == recurso_id)
        if admin_id:
            stmt = stmt.where(AuditLog.admin_id == admin_id)
        stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        return list(await self.db.scalars(stmt))
