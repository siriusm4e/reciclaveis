"""Repositórios — Conta, Membro, PapelAtivado, Estabelecimento, ConviteMembro."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from app.models.conta import Conta
from app.models.convite import ConviteMembro
from app.models.enums import ConviteStatus, PapelInternoMembro, PapelTipo
from app.models.estabelecimento import Estabelecimento
from app.models.membro import Membro
from app.models.papel import PapelAtivado
from app.repositories.base import BaseRepository


class ContaRepository(BaseRepository[Conta]):
    model = Conta

    async def get_by_cnpj(self, cnpj: str) -> Conta | None:
        return await self.db.scalar(select(Conta).where(Conta.cnpj == cnpj))

    async def listar_para_usuario(self, usuario_id: UUID) -> list[Conta]:
        stmt = (
            select(Conta)
            .join(Membro, Membro.conta_id == Conta.id)
            .where(Membro.usuario_id == usuario_id)
        )
        return list(await self.db.scalars(stmt))


class MembroRepository(BaseRepository[Membro]):
    model = Membro

    async def get_de_usuario_em_conta(
        self, usuario_id: UUID, conta_id: UUID
    ) -> Membro | None:
        return await self.db.scalar(
            select(Membro).where(Membro.usuario_id == usuario_id, Membro.conta_id == conta_id)
        )

    async def listar_da_conta(self, conta_id: UUID) -> list[Membro]:
        return list(await self.db.scalars(select(Membro).where(Membro.conta_id == conta_id)))

    async def contar_admins(self, conta_id: UUID) -> int:
        from sqlalchemy import func

        return int(
            await self.db.scalar(
                select(func.count())
                .select_from(Membro)
                .where(
                    Membro.conta_id == conta_id,
                    Membro.papel_interno == PapelInternoMembro.ADMIN,
                )
            )
            or 0
        )


class PapelRepository(BaseRepository[PapelAtivado]):
    model = PapelAtivado

    async def listar_da_conta(self, conta_id: UUID) -> list[PapelAtivado]:
        return list(
            await self.db.scalars(
                select(PapelAtivado).where(PapelAtivado.conta_id == conta_id)
            )
        )

    async def get_da_conta_por_tipo(
        self, conta_id: UUID, papel: PapelTipo
    ) -> PapelAtivado | None:
        return await self.db.scalar(
            select(PapelAtivado).where(
                PapelAtivado.conta_id == conta_id, PapelAtivado.papel == papel
            )
        )


class EstabelecimentoRepository(BaseRepository[Estabelecimento]):
    model = Estabelecimento

    async def listar_da_conta(self, conta_id: UUID) -> list[Estabelecimento]:
        return list(
            await self.db.scalars(
                select(Estabelecimento).where(Estabelecimento.conta_id == conta_id)
            )
        )


class ConviteRepository(BaseRepository[ConviteMembro]):
    model = ConviteMembro

    async def get_pendente_por_email_conta(
        self, conta_id: UUID, email: str
    ) -> ConviteMembro | None:
        return await self.db.scalar(
            select(ConviteMembro).where(
                ConviteMembro.conta_id == conta_id,
                ConviteMembro.email == email,
                ConviteMembro.status == ConviteStatus.PENDENTE,
            )
        )

    async def get_por_token(self, token: str) -> ConviteMembro | None:
        return await self.db.scalar(
            select(ConviteMembro).where(ConviteMembro.token == token)
        )

    async def expirar_vencidos(self) -> int:
        from sqlalchemy import update

        stmt = (
            update(ConviteMembro)
            .where(
                ConviteMembro.status == ConviteStatus.PENDENTE,
                ConviteMembro.expira_em < datetime.now(tz=timezone.utc),
            )
            .values(status=ConviteStatus.EXPIRADO)
            .execution_options(synchronize_session=False)
        )
        r = await self.db.execute(stmt)
        return r.rowcount or 0
