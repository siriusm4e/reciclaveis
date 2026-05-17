"""Repositórios — ConteudoEducativo, PreferenciaComunicacao, Dispositivo."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.conteudo_educativo import ConteudoEducativo
from app.models.dispositivo import Dispositivo
from app.models.preferencia_comunicacao import PreferenciaComunicacao
from app.repositories.base import BaseRepository


class ConteudoEducativoRepository(BaseRepository[ConteudoEducativo]):
    model = ConteudoEducativo

    async def listar_publicados(
        self,
        *,
        papel_slug: str | None = None,
        categoria_slug: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ConteudoEducativo]:
        stmt = select(ConteudoEducativo).where(ConteudoEducativo.publicado.is_(True))
        if papel_slug:
            stmt = stmt.where(
                (ConteudoEducativo.papeis_alvo == [])
                | (ConteudoEducativo.papeis_alvo.op("?")(papel_slug))
            )
        if categoria_slug:
            stmt = stmt.where(
                (ConteudoEducativo.categorias_alvo == [])
                | (ConteudoEducativo.categorias_alvo.op("?")(categoria_slug))
            )
        stmt = stmt.order_by(ConteudoEducativo.created_at.desc()).limit(limit).offset(offset)
        return list(await self.db.scalars(stmt))


class PreferenciaRepository(BaseRepository[PreferenciaComunicacao]):
    model = PreferenciaComunicacao

    async def get_da_conta(self, conta_id: UUID) -> PreferenciaComunicacao | None:
        return await self.db.scalar(
            select(PreferenciaComunicacao).where(PreferenciaComunicacao.conta_id == conta_id)
        )

    async def upsert(self, conta_id: UUID, **prefs) -> PreferenciaComunicacao:
        pref = await self.get_da_conta(conta_id)
        if pref is None:
            pref = PreferenciaComunicacao(conta_id=conta_id, **prefs)
            self.db.add(pref)
        else:
            for k, v in prefs.items():
                if v is not None:
                    setattr(pref, k, v)
        await self.db.flush()
        return pref


class DispositivoRepository(BaseRepository[Dispositivo]):
    model = Dispositivo

    async def upsert_token(
        self,
        *,
        usuario_id: UUID,
        plataforma: str,
        token: str,
        modelo: str | None = None,
        versao_app: str | None = None,
    ) -> Dispositivo:
        existing = await self.db.scalar(select(Dispositivo).where(Dispositivo.token == token))
        if existing:
            existing.usuario_id = usuario_id
            existing.plataforma = plataforma
            existing.modelo = modelo
            existing.versao_app = versao_app
            existing.ativo = True
            await self.db.flush()
            return existing
        d = Dispositivo(
            usuario_id=usuario_id,
            plataforma=plataforma,
            token=token,
            modelo=modelo,
            versao_app=versao_app,
        )
        self.db.add(d)
        await self.db.flush()
        return d

    async def tokens_ativos_de_conta(self, conta_id: UUID) -> list[str]:
        """Tokens push de todos os Usuarios vinculados à Conta."""
        from app.models.membro import Membro

        rows = await self.db.scalars(
            select(Dispositivo.token)
            .join(Membro, Membro.usuario_id == Dispositivo.usuario_id)
            .where(Membro.conta_id == conta_id, Dispositivo.ativo.is_(True))
        )
        return [t for t in rows]
