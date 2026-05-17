"""Regras de identidade — Conta, Membro, Papel, Convite, validação de imutabilidade."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    TipoContaImutavelError,
    ValidationDomainError,
)
from app.core.security import generate_opaque_token
from app.models.conta import Conta, ContaStatus, ContaTipo
from app.models.convite import ConviteMembro
from app.models.enums import (
    ConviteStatus,
    PapelInternoMembro,
    PapelStatus,
    PapelTipo,
)
from app.models.estabelecimento import Estabelecimento
from app.models.membro import Membro
from app.models.papel import PapelAtivado
from app.models.preferencia_comunicacao import PreferenciaComunicacao
from app.models.usuario import Usuario
from app.models.vinculo_detectado import VinculoDetectado
from app.models.enums import VinculoMotivo
from app.repositories.conta import (
    ContaRepository,
    ConviteRepository,
    EstabelecimentoRepository,
    MembroRepository,
    PapelRepository,
)
from app.repositories.usuario import UsuarioRepository
from app.utils.geo import make_point_wkt
from app.utils.receita_federal import get_provider


class IdentidadeService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.contas = ContaRepository(db)
        self.membros = MembroRepository(db)
        self.papeis = PapelRepository(db)
        self.estabelecimentos = EstabelecimentoRepository(db)
        self.convites = ConviteRepository(db)
        self.usuarios = UsuarioRepository(db)

    # === Conta ===

    async def criar_conta(
        self,
        *,
        usuario: Usuario,
        tipo: ContaTipo,
        nome_publico: str,
        cnpj: str | None = None,
        escopo_territorial: dict | None = None,
    ) -> Conta:
        # Validações por tipo
        if tipo == ContaTipo.PF and cnpj:
            raise ValidationDomainError("Conta PF não pode ter CNPJ")
        if tipo in (ContaTipo.PJ_PRIVADA, ContaTipo.ORGAO_PUBLICO) and not cnpj:
            raise ValidationDomainError("CNPJ é obrigatório para PJ/Órgão")

        if cnpj:
            existing = await self.contas.get_by_cnpj(cnpj)
            if existing:
                raise ConflictError("CNPJ já cadastrado")
            data = await get_provider().consultar_cnpj(cnpj)
            if data.situacao != "ativa":
                raise ValidationDomainError(
                    "CNPJ com situação não permitida", details={"situacao": data.situacao}
                )

        if tipo == ContaTipo.ORGAO_PUBLICO and not escopo_territorial:
            raise ValidationDomainError("Órgão Público requer escopo territorial")

        # Status inicial: pendente (PF/PJ ativam após onboarding); órgão público fica em_revisao
        status_inicial = (
            ContaStatus.EM_REVISAO if tipo == ContaTipo.ORGAO_PUBLICO else ContaStatus.PENDENTE
        )

        conta = Conta(
            tipo=tipo,
            status=status_inicial,
            nome_publico=nome_publico,
            cnpj=cnpj,
            escopo_territorial=escopo_territorial,
        )
        self.db.add(conta)
        await self.db.flush()

        # Membro admin único
        self.db.add(
            Membro(
                usuario_id=usuario.id,
                conta_id=conta.id,
                papel_interno=PapelInternoMembro.ADMIN,
            )
        )
        # PreferenciaComunicacao default
        self.db.add(PreferenciaComunicacao(conta_id=conta.id))

        await self.db.flush()
        return conta

    async def atualizar_conta(
        self, conta: Conta, *, nome_publico: str | None = None, **outros
    ) -> Conta:
        if nome_publico:
            conta.nome_publico = nome_publico
        for k, v in outros.items():
            if v is not None and hasattr(conta, k):
                setattr(conta, k, v)
        await self.db.flush()
        return conta

    async def mudar_status(
        self, conta: Conta, *, novo: ContaStatus, motivo: str
    ) -> Conta:
        if conta.status == ContaStatus.ANONIMIZADA:
            raise ConflictError("Conta já anonimizada")
        conta.status = novo
        await self.db.flush()
        # AuditLog gravado pelo caller (route admin) com admin_id e request
        return conta

    async def trocar_tipo(self, _conta: Conta, _novo: ContaTipo) -> Conta:
        # Regra absoluta: Tipo é imutável após criação
        raise TipoContaImutavelError("Tipo de Conta é imutável")

    # === Membro / Convite ===

    async def listar_membros(self, conta_id: UUID) -> list[Membro]:
        return await self.membros.listar_da_conta(conta_id)

    async def convidar_membro(
        self,
        *,
        conta: Conta,
        email: str,
        papel_interno: PapelInternoMembro,
        convidado_por_usuario_id: UUID,
    ) -> ConviteMembro:
        if conta.tipo == ContaTipo.PF:
            raise ConflictError("Conta PF tem admin único — não aceita convites")

        # Segundo convite para o mesmo e-mail substitui o anterior
        existente = await self.convites.get_pendente_por_email_conta(conta.id, email)
        if existente:
            existente.status = ConviteStatus.CANCELADO

        convite = ConviteMembro(
            conta_id=conta.id,
            email=email,
            papel_interno=papel_interno,
            token=generate_opaque_token(),
            expira_em=datetime.now(tz=timezone.utc) + timedelta(hours=48),
            convidado_por_usuario_id=convidado_por_usuario_id,
        )
        self.db.add(convite)
        await self.db.flush()
        return convite

    async def remover_membro(self, *, conta_id: UUID, membro_id: UUID) -> None:
        from sqlalchemy import select

        membro = await self.db.scalar(
            select(Membro).where(Membro.id == membro_id, Membro.conta_id == conta_id)
        )
        if membro is None:
            raise NotFoundError("Membro não encontrado")

        if membro.papel_interno == PapelInternoMembro.ADMIN:
            admins = await self.membros.contar_admins(conta_id)
            if admins <= 1:
                raise ConflictError("Conta deve manter ao menos 1 admin")

        await self.db.delete(membro)
        await self.db.flush()

    # === Papel ===

    async def ativar_papel(
        self,
        *,
        conta: Conta,
        papel: PapelTipo,
        dados: dict | None = None,
    ) -> PapelAtivado:
        existing = await self.papeis.get_da_conta_por_tipo(conta.id, papel)
        if existing:
            raise ConflictError("Papel já ativado nesta Conta")

        # Regras por tipo de Conta — Prefeitura/Órgão Estadual só em Conta órgão público.
        if papel in (PapelTipo.PREFEITURA, PapelTipo.ORGAO_ESTADUAL) and conta.tipo != ContaTipo.ORGAO_PUBLICO:
            raise ValidationDomainError(
                "Papéis Prefeitura/Órgão Estadual exigem Conta tipo Órgão Público"
            )

        papel_obj = PapelAtivado(
            conta_id=conta.id,
            papel=papel,
            status=PapelStatus.PENDENTE,
            dados_complementares=dados or {},
        )
        self.db.add(papel_obj)
        await self.db.flush()
        return papel_obj

    async def listar_papeis(self, conta_id: UUID) -> list[PapelAtivado]:
        return await self.papeis.listar_da_conta(conta_id)

    async def atualizar_papel(
        self,
        *,
        papel: PapelAtivado,
        dados: dict | None = None,
        status: PapelStatus | None = None,
    ) -> PapelAtivado:
        if dados is not None:
            papel.dados_complementares = dados
        if status is not None:
            papel.status = status
        await self.db.flush()
        return papel

    # === Estabelecimento ===

    async def criar_estabelecimento(
        self,
        *,
        conta: Conta,
        nome: str,
        cep: str,
        logradouro: str,
        numero: str,
        complemento: str | None,
        bairro: str,
        cidade: str,
        uf: str,
        ibge_municipio: str | None,
        lat: float,
        lng: float,
    ) -> Estabelecimento:
        if conta.tipo == ContaTipo.PF:
            raise ConflictError("Conta PF não possui Estabelecimentos")

        est = Estabelecimento(
            conta_id=conta.id,
            nome=nome,
            cep=cep,
            logradouro=logradouro,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            uf=uf,
            ibge_municipio=ibge_municipio,
            geom=make_point_wkt(lat, lng),
        )
        self.db.add(est)
        await self.db.flush()
        return est

    # === Detecção de vínculo (chamada quando uma nova Conta é criada / Membro adicionado) ===

    async def detectar_vinculos(self, conta: Conta) -> int:
        """Marca VinculoDetectado quando outra Conta compartilha telefone/CPF/CNPJ.

        Retorna número de vínculos criados.
        """
        from sqlalchemy import select

        criados = 0
        usuarios = await self.db.scalars(
            select(Usuario)
            .join(Membro, Membro.usuario_id == Usuario.id)
            .where(Membro.conta_id == conta.id)
        )
        for u in usuarios:
            # Outras Contas com membros do mesmo CPF
            outros = await self.db.scalars(
                select(Membro.conta_id).where(
                    Membro.usuario_id == u.id, Membro.conta_id != conta.id
                )
            )
            for outra_conta_id in outros:
                if not await self._existe_vinculo(conta.id, outra_conta_id):
                    self.db.add(
                        VinculoDetectado(
                            conta_a_id=conta.id,
                            conta_b_id=outra_conta_id,
                            motivo=VinculoMotivo.MESMO_CPF_RESPONSAVEL,
                        )
                    )
                    criados += 1
            # Telefone duplicado
            if u.telefone:
                outros_tel = await self.db.scalars(
                    select(Membro.conta_id)
                    .join(Usuario, Usuario.id == Membro.usuario_id)
                    .where(Usuario.telefone == u.telefone, Membro.conta_id != conta.id)
                )
                for outra_conta_id in outros_tel:
                    if not await self._existe_vinculo(conta.id, outra_conta_id):
                        self.db.add(
                            VinculoDetectado(
                                conta_a_id=conta.id,
                                conta_b_id=outra_conta_id,
                                motivo=VinculoMotivo.MESMO_TELEFONE,
                            )
                        )
                        criados += 1
        await self.db.flush()
        return criados

    async def _existe_vinculo(self, a: UUID, b: UUID) -> bool:
        from sqlalchemy import or_, and_, select

        return bool(
            await self.db.scalar(
                select(VinculoDetectado).where(
                    or_(
                        and_(
                            VinculoDetectado.conta_a_id == a,
                            VinculoDetectado.conta_b_id == b,
                        ),
                        and_(
                            VinculoDetectado.conta_a_id == b,
                            VinculoDetectado.conta_b_id == a,
                        ),
                    )
                )
            )
        )


__all__ = ["IdentidadeService"]
_ = settings  # mantém import vivo se algum futuro flag depender
