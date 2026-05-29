"""Seed extra de demonstração — admin "rodrigo" + mais pins no mapa.

    docker compose exec backend python -m app.scripts.seed_demo_extra

Cria (idempotente):
  - Usuário rodrigo.lobo@me.com com PerfilInterno SUPERADMIN (todos os privilégios)
  - +6 anúncios de venda do catador (materiais/coords variados em Curitiba)
  - +5 ofertas de compra do comprador (materiais/coords variados em Curitiba)

Requer: seed básico + seed_demo já executados (usa as contas catador/comprador).
"""

from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.conta import Conta
from app.models.enums import (
    ContaTipo,
    PapelTipo,
    PerfilInternoTipo,
    TransacaoTipo,
)
from app.models.membro import Membro
from app.models.papel import PapelAtivado
from app.models.perfil_interno import PerfilInterno
from app.models.transacao_credito import TransacaoCredito
from app.models.usuario import Usuario
from app.scripts.seed_demo import (
    _get_or_create_anuncio,
    _get_or_create_conta,
    _get_or_create_oferta,
    _get_or_create_papel,
    _aprovar_documento,
    _tipo_material_por_slug,
)

log = structlog.get_logger(__name__)


# Coordenadas extras espalhadas por Curitiba/RMC para popular o mapa
COORDS_VENDA_EXTRA = [
    ("pead-colorido", Decimal("1.80"), Decimal("40"), -25.3935, -49.2680),   # Cabral
    ("pp-balde", Decimal("2.10"), Decimal("25"), -25.4612, -49.3020),        # Portão
    ("cobre-mel", Decimal("38.00"), Decimal("8"), -25.4188, -49.2680),       # Juvevê
    ("aco-ferro", Decimal("0.85"), Decimal("300"), -25.4760, -49.2520),      # Hauer
    ("papel-branco", Decimal("1.20"), Decimal("60"), -25.4012, -49.3100),    # Santa Felicidade
    ("tetra-pak", Decimal("0.70"), Decimal("45"), -25.4925, -49.2890),       # Fazendinha
]

COORDS_OFERTA_EXTRA = [
    ("aco-ferro", "Compro sucata de aço/ferro", "Pago à vista, retiro no local. Acima de 200kg.",
     Decimal("0.95"), Decimal("200"), 70, -25.4480, -49.3300),              # Novo Mundo
    ("cobre-mel", "Compro cobre mel — melhor preço", "Cobre limpo, sem queima. Pago no PIX.",
     Decimal("42.00"), Decimal("5"), 90, -25.4300, -49.2600),               # Centro Cívico
    ("pead-colorido", "Compro PEAD colorido", "Bombonas e baldes triturados ou inteiros.",
     Decimal("2.40"), Decimal("100"), 60, -25.5020, -49.3100),              # Pinheirinho
    ("vidro-incolor", "Compro vidro incolor", "Cacos ou inteiro, mínimo 100kg.",
     Decimal("0.45"), Decimal("100"), 50, -25.4150, -49.2950),              # Mercês
    ("aluminio-chapa", "Compro alumínio chapa", "Perfil e chaparia, pago por kg.",
     Decimal("11.50"), Decimal("20"), 80, -25.4680, -49.2400),              # Cajuru
]


# Papéis que o rodrigo terá ativos (cobre visão de vendedor e comprador no mapa)
RODRIGO_PAPEIS = [PapelTipo.COMPRADOR, PapelTipo.CATADOR, PapelTipo.GESTOR_RESIDUOS]


async def _seed_rodrigo_superadmin(db: AsyncSession) -> Usuario:
    email = "rodrigo.lobo@me.com"
    u = await db.scalar(select(Usuario).where(Usuario.email == email))
    if u is None:
        u = Usuario(
            cpf="98765432100",
            email=email,
            email_confirmado=True,
            senha_hash=hash_password("fdra775"),
            nome_completo="Rodrigo Lobo",
            telefone=None,
            ativo=True,
        )
        db.add(u)
        await db.flush()
        log.info("seed_extra_rodrigo_criado", email=email)
    else:
        # Garante senha e estado mesmo se já existia
        u.senha_hash = hash_password("fdra775")
        u.ativo = True
        u.email_confirmado = True
        log.info("seed_extra_rodrigo_ja_existe", email=email)

    perfil = await db.scalar(select(PerfilInterno).where(PerfilInterno.usuario_id == u.id))
    if perfil is None:
        db.add(PerfilInterno(usuario_id=u.id, tipo=PerfilInternoTipo.SUPERADMIN, ativo=True))
    else:
        perfil.tipo = PerfilInternoTipo.SUPERADMIN
        perfil.ativo = True
    await db.flush()
    return u


async def _seed_rodrigo_conta(db: AsyncSession, *, usuario: Usuario) -> None:
    """Conta PJ completa para o rodrigo ver o app de consumidor + o mapa.

    Superadmin não tem Conta por padrão; aqui damos uma para que ele também
    participe do marketplace (mapa, papéis, créditos)."""
    conta = await _get_or_create_conta(
        db,
        usuario=usuario,
        tipo=ContaTipo.PJ_PRIVADA,
        nome_publico="Rodrigo Lobo — Demo",
        cnpj="12345678000195",
    )
    # Papéis ativos (vendedor + comprador + gestor) → vê pins dos dois lados
    for papel in RODRIGO_PAPEIS:
        await _get_or_create_papel(db, conta=conta, papel=papel)

    # Documentos básicos de PJ aprovados (libera fluxos)
    for slug in ("cnpj_ativo", "contrato_social"):
        await _aprovar_documento(db, conta=conta, tipo_slug=slug)

    # Créditos para usar recursos pagos na demo
    existing = await db.scalar(
        select(TransacaoCredito).where(
            TransacaoCredito.conta_id == conta.id, TransacaoCredito.tipo == TransacaoTipo.COMPRA
        )
    )
    if existing is None:
        db.add(
            TransacaoCredito(
                conta_id=conta.id,
                tipo=TransacaoTipo.COMPRA,
                valor=500,
                descricao="Saldo de demonstração (rodrigo)",
                referencia_tipo="pacote_credito",
            )
        )
    await db.flush()


async def _conta_papel_de(
    db: AsyncSession, *, email: str, papel: PapelTipo
) -> tuple[Optional[Conta], Optional[PapelAtivado]]:
    u = await db.scalar(select(Usuario).where(Usuario.email == email))
    if u is None:
        return None, None
    conta = await db.scalar(
        select(Conta).join(Membro, Membro.conta_id == Conta.id).where(Membro.usuario_id == u.id)
    )
    if conta is None:
        return None, None
    p = await db.scalar(
        select(PapelAtivado).where(PapelAtivado.conta_id == conta.id, PapelAtivado.papel == papel)
    )
    return conta, p


async def run() -> None:
    async with SessionLocal() as db:
        try:
            log.info("seed_demo_extra_inicio")
            rodrigo = await _seed_rodrigo_superadmin(db)
            await _seed_rodrigo_conta(db, usuario=rodrigo)
            log.info("seed_extra_superadmin_ok")

            conta_cat, papel_cat = await _conta_papel_de(
                db, email="catador@pnr.com.br", papel=PapelTipo.CATADOR
            )
            conta_comp, papel_comp = await _conta_papel_de(
                db, email="comprador@pnr.com.br", papel=PapelTipo.COMPRADOR
            )

            criados_v = 0
            if conta_cat and papel_cat:
                for slug, preco, vol, lat, lng in COORDS_VENDA_EXTRA:
                    tipo = await _tipo_material_por_slug(db, slug)
                    if tipo is None:
                        log.warning("seed_extra_material_ausente", slug=slug)
                        continue
                    from app.models.enums import FrequenciaAnuncio

                    await _get_or_create_anuncio(
                        db, conta=conta_cat, papel=papel_cat, tipo=tipo,
                        preco=preco, volume=vol,
                        frequencia=FrequenciaAnuncio.LOTE_UNICO, intervalo=None,
                        lat=lat, lng=lng,
                        condicao_limpeza="limpo", condicao_umidade="seco", condicao_forma="solto",
                    )
                    criados_v += 1
            log.info("seed_extra_anuncios_ok", count=criados_v)

            criados_o = 0
            if conta_comp and papel_comp:
                for slug, titulo, desc, preco, vmin, raio, lat, lng in COORDS_OFERTA_EXTRA:
                    tipo = await _tipo_material_por_slug(db, slug)
                    if tipo is None:
                        log.warning("seed_extra_material_ausente", slug=slug)
                        continue
                    await _get_or_create_oferta(
                        db, conta=conta_comp, papel=papel_comp, tipo=tipo,
                        titulo=titulo, descricao=desc,
                        preco=preco, vol_min=vmin, vol_max=None,
                        volume_minimo_kg=float(vmin),
                        condicao_limpeza="limpo", condicao_umidade="seco", condicao_forma=None,
                        raio_km=raio, retira=True, lat=lat, lng=lng, boost_ativo=False,
                    )
                    criados_o += 1
            log.info("seed_extra_ofertas_ok", count=criados_o)

            await db.commit()
            log.info("seed_demo_extra_concluido", anuncios=criados_v, ofertas=criados_o)
        except Exception:
            await db.rollback()
            raise


def main() -> None:
    from app.core.logging import configure_logging

    configure_logging()
    asyncio.run(run())


if __name__ == "__main__":
    main()
