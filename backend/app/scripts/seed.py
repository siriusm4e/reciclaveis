"""Seed inicial — execute com:

    docker compose exec backend python -m app.scripts.seed

Idempotente: roda múltiplas vezes sem duplicar (faz upsert por slug/nome).
"""

from __future__ import annotations

import asyncio
from typing import Iterable

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.categoria import Categoria
from app.models.enums import (
    DocumentoEscopo,
    PerfilInternoTipo,
    PapelTipo,
)
from app.models.pacote_credito import PacoteCredito
from app.models.perfil_interno import PerfilInterno
from app.models.plano import Plano
from app.models.subcategoria import Subcategoria
from app.models.tipo_documento import TipoDocumento
from app.models.usuario import Usuario

log = structlog.get_logger(__name__)


# =============================================================================
# Categorias e Subcategorias do catálogo nacional
# =============================================================================

CATALOGO: list[dict] = [
    {
        "nome": "Metais",
        "slug": "metais",
        "cor_hex": "#5c5a52",
        "icone": "wrench",
        "ordem": 10,
        "subcategorias": [
            ("Alumínio (latinha)", "aluminio-latinha", "kg"),
            ("Alumínio chaparia", "aluminio-chaparia", "kg"),
            ("Cobre", "cobre", "kg"),
            ("Aço/Ferro", "aco-ferro", "kg"),
            ("Sucata mista", "sucata-mista", "kg"),
        ],
    },
    {
        "nome": "Plásticos",
        "slug": "plasticos",
        "cor_hex": "#dc2626",
        "icone": "box",
        "ordem": 20,
        "subcategorias": [
            ("PET cristal", "pet-cristal", "kg"),
            ("PET verde", "pet-verde", "kg"),
            ("PEAD (rígido)", "pead", "kg"),
            ("PP", "pp", "kg"),
            ("PVC", "pvc", "kg"),
            ("Filme PEBD", "filme-pebd", "kg"),
        ],
    },
    {
        "nome": "Papéis",
        "slug": "papeis",
        "cor_hex": "#3b82f6",
        "icone": "file-text",
        "ordem": 30,
        "subcategorias": [
            ("Papelão", "papelao", "kg"),
            ("Papel branco (off-set)", "papel-branco", "kg"),
            ("Papel misto", "papel-misto", "kg"),
            ("Jornal/revista", "jornal-revista", "kg"),
            ("Tetra Pak (longa vida)", "tetra-pak", "kg"),
        ],
    },
    {
        "nome": "Vidros",
        "slug": "vidros",
        "cor_hex": "#10b981",
        "icone": "wine",
        "ordem": 40,
        "subcategorias": [
            ("Vidro incolor", "vidro-incolor", "kg"),
            ("Vidro âmbar", "vidro-ambar", "kg"),
            ("Vidro verde", "vidro-verde", "kg"),
            ("Vidro plano", "vidro-plano", "kg"),
        ],
    },
    {
        "nome": "Óleos",
        "slug": "oleos",
        "cor_hex": "#f59e0b",
        "icone": "droplet",
        "ordem": 50,
        "subcategorias": [
            ("Óleo de cozinha usado", "oleo-cozinha-usado", "l"),
            ("Óleo lubrificante usado", "oleo-lubrificante-usado", "l"),
        ],
    },
    {
        "nome": "Eletrônicos",
        "slug": "eletronicos",
        "cor_hex": "#8b5cf6",
        "icone": "cpu",
        "ordem": 60,
        "subcategorias": [
            ("Placas (PCI)", "placas-pci", "kg"),
            ("Cabos e fios", "cabos-fios", "kg"),
            ("Eletrodomésticos (linha branca)", "linha-branca", "unidade"),
            ("Telefonia/celular", "celular", "unidade"),
        ],
    },
    {
        "nome": "Construção civil",
        "slug": "construcao-civil",
        "cor_hex": "#6b7280",
        "icone": "hammer",
        "ordem": 70,
        "subcategorias": [
            ("Entulho misto", "entulho-misto", "m3"),
            ("Concreto", "concreto", "m3"),
            ("Madeira de obra", "madeira-obra", "m3"),
            ("Gesso", "gesso", "kg"),
        ],
    },
    {
        "nome": "Têxteis",
        "slug": "texteis",
        "cor_hex": "#ec4899",
        "icone": "shirt",
        "ordem": 80,
        "subcategorias": [
            ("Algodão (retalho)", "algodao-retalho", "kg"),
            ("Tecido misto", "tecido-misto", "kg"),
        ],
    },
    {
        "nome": "Automotivo",
        "slug": "automotivo",
        "cor_hex": "#0ea5e9",
        "icone": "car",
        "ordem": 90,
        "subcategorias": [
            ("Pneus", "pneus", "unidade"),
            ("Baterias chumbo-ácido", "bateria-chumbo", "kg"),
            ("Catalisadores", "catalisadores", "unidade"),
        ],
    },
    {
        "nome": "Orgânicos",
        "slug": "organicos",
        "cor_hex": "#22c55e",
        "icone": "leaf",
        "ordem": 100,
        "subcategorias": [
            ("Restos de poda", "restos-poda", "m3"),
            ("Compostáveis", "compostaveis", "kg"),
        ],
    },
    {
        "nome": "Hospitalar (regulado)",
        "slug": "hospitalar",
        "cor_hex": "#dc2626",
        "icone": "alert-triangle",
        "ordem": 110,
        "subcategorias": [
            ("Grupo A — infectante", "hospitalar-a-infectante", "kg", True, ["licenca_ambiental", "cadri"]),
            ("Grupo E — perfurocortante", "hospitalar-e-perfurocortante", "kg", True, ["licenca_ambiental", "cadri"]),
        ],
    },
    {
        "nome": "Químicos (regulado)",
        "slug": "quimicos",
        "cor_hex": "#7f1d1d",
        "icone": "flask-conical",
        "ordem": 120,
        "subcategorias": [
            ("Solventes orgânicos", "solventes-organicos", "l", True, ["licenca_ambiental", "cadri", "mtr"]),
            ("Tintas industriais", "tintas-industriais", "l", True, ["licenca_ambiental"]),
        ],
    },
    {
        "nome": "Pallets",
        "slug": "pallets",
        "cor_hex": "#a16207",
        "icone": "package",
        "ordem": 130,
        "subcategorias": [
            ("Pallet PBR padrão", "pallet-pbr", "unidade"),
            ("Pallet descartável", "pallet-descartavel", "unidade"),
        ],
    },
]


async def _seed_categorias(db: AsyncSession) -> None:
    for cat_def in CATALOGO:
        cat = await db.scalar(select(Categoria).where(Categoria.slug == cat_def["slug"]))
        if cat is None:
            cat = Categoria(
                nome=cat_def["nome"],
                slug=cat_def["slug"],
                cor_hex=cat_def["cor_hex"],
                icone=cat_def["icone"],
                ordem=cat_def["ordem"],
                ativo=True,
            )
            db.add(cat)
            await db.flush()
        for idx, sub_def in enumerate(cat_def["subcategorias"]):
            nome, slug, unidade = sub_def[0], sub_def[1], sub_def[2]
            regulada = sub_def[3] if len(sub_def) > 3 else False
            docs = sub_def[4] if len(sub_def) > 4 else []
            existing = await db.scalar(
                select(Subcategoria).where(
                    Subcategoria.categoria_id == cat.id, Subcategoria.slug == slug
                )
            )
            if existing is None:
                db.add(
                    Subcategoria(
                        categoria_id=cat.id,
                        nome=nome,
                        slug=slug,
                        unidade_padrao=unidade,
                        requer_validacao_documental=regulada,
                        documentos_exigidos=list(docs),
                        atributos_especificos={},
                        ordem=10 * (idx + 1),
                        ativo=True,
                    )
                )
    await db.flush()


# =============================================================================
# Tipos de Documento padrão
# =============================================================================

TIPOS_DOC: list[dict] = [
    {
        "slug": "cnpj_ativo",
        "nome": "Cartão CNPJ ativo",
        "escopo": DocumentoEscopo.CONTA,
        "papeis_aplicaveis": [],
        "tem_vencimento": False,
        "exige_aprovacao_manual": True,
        "obrigatorio": True,
    },
    {
        "slug": "contrato_social",
        "nome": "Contrato social",
        "escopo": DocumentoEscopo.CONTA,
        "papeis_aplicaveis": [],
        "tem_vencimento": False,
        "exige_aprovacao_manual": True,
        "obrigatorio": True,
    },
    {
        "slug": "licenca_ambiental",
        "nome": "Licença ambiental de operação",
        "escopo": DocumentoEscopo.ESTABELECIMENTO,
        "papeis_aplicaveis": [
            PapelTipo.GESTOR_RESIDUOS.value,
            PapelTipo.COMPRADOR.value,
            PapelTipo.PRESTADOR_SERVICO.value,
        ],
        "tem_vencimento": True,
        "exige_aprovacao_manual": True,
        "obrigatorio": False,
    },
    {
        "slug": "cadri",
        "nome": "CADRI (Cetesb)",
        "escopo": DocumentoEscopo.ESTABELECIMENTO,
        "papeis_aplicaveis": [
            PapelTipo.GESTOR_RESIDUOS.value,
            PapelTipo.COMPRADOR.value,
        ],
        "tem_vencimento": True,
        "exige_aprovacao_manual": True,
        "obrigatorio": False,
    },
    {
        "slug": "mtr",
        "nome": "Manifesto de Transporte de Resíduos (MTR)",
        "escopo": DocumentoEscopo.CONTA,
        "papeis_aplicaveis": [PapelTipo.FRETEIRO.value, PapelTipo.GESTOR_RESIDUOS.value],
        "tem_vencimento": True,
        "exige_aprovacao_manual": True,
        "obrigatorio": False,
    },
    {
        "slug": "antt",
        "nome": "ANTT — Cadastro de transportador",
        "escopo": DocumentoEscopo.CONTA,
        "papeis_aplicaveis": [PapelTipo.FRETEIRO.value],
        "tem_vencimento": True,
        "exige_aprovacao_manual": True,
        "obrigatorio": False,
    },
    {
        "slug": "alvara_funcionamento",
        "nome": "Alvará de funcionamento",
        "escopo": DocumentoEscopo.ESTABELECIMENTO,
        "papeis_aplicaveis": [],
        "tem_vencimento": True,
        "exige_aprovacao_manual": True,
        "obrigatorio": False,
    },
    {
        "slug": "selfie_documento",
        "nome": "Selfie com documento (PF)",
        "escopo": DocumentoEscopo.CONTA,
        "papeis_aplicaveis": [PapelTipo.CATADOR.value, PapelTipo.COLETOR.value],
        "tem_vencimento": False,
        "exige_aprovacao_manual": True,
        "obrigatorio": False,
    },
]


async def _seed_tipos_documento(db: AsyncSession) -> None:
    for t in TIPOS_DOC:
        existing = await db.scalar(select(TipoDocumento).where(TipoDocumento.slug == t["slug"]))
        if existing is None:
            db.add(TipoDocumento(**t, ativo=True))
    await db.flush()


# =============================================================================
# Planos por Papel — todos com plano gratuito; alguns com pago superior
# =============================================================================

def _planos_padrao() -> Iterable[dict]:
    """Plano gratuito + pago para cada papel marketplaceable."""
    papeis = [
        PapelTipo.CATADOR,
        PapelTipo.COLETOR,
        PapelTipo.ACUMULADOR,
        PapelTipo.COMPRADOR,
        PapelTipo.GESTOR_RESIDUOS,
        PapelTipo.PRESTADOR_SERVICO,
        PapelTipo.FRETEIRO,
        PapelTipo.REVENDEDOR_EQUIPAMENTOS,
        PapelTipo.GERADOR_INDUSTRIAL,
    ]
    for p in papeis:
        yield {
            "papel": p,
            "nome": "Gratuito",
            "descricao": "Plano gratuito padrão.",
            "limite_publicacoes_ativas": 3,
            "permite_alerta_pago": False,
            "preco_mensal_centavos": 0,
            "gratuito": True,
        }
        yield {
            "papel": p,
            "nome": "Profissional",
            "descricao": "Mais publicações simultâneas + Alerta Pago.",
            "limite_publicacoes_ativas": 50,
            "permite_alerta_pago": True,
            "preco_mensal_centavos": 4990,
            "gratuito": False,
        }
    # Anuidade institucional (Órgão Público): registrada para Prefeitura/Órgão Estadual
    for p in (PapelTipo.PREFEITURA, PapelTipo.ORGAO_ESTADUAL):
        yield {
            "papel": p,
            "nome": "Anuidade Institucional",
            "descricao": "Anuidade via empenho público.",
            "limite_publicacoes_ativas": 200,
            "permite_alerta_pago": False,
            "preco_mensal_centavos": 0,
            "gratuito": True,
        }


async def _seed_planos(db: AsyncSession) -> None:
    for plano_def in _planos_padrao():
        existing = await db.scalar(
            select(Plano).where(Plano.papel == plano_def["papel"], Plano.nome == plano_def["nome"])
        )
        if existing is None:
            db.add(Plano(**plano_def, ativo=True))
    await db.flush()


# =============================================================================
# Pacotes de Crédito
# =============================================================================

PACOTES: list[dict] = [
    {"nome": "Starter", "creditos": 50, "bonus": 0, "preco_centavos": 4990, "ordem": 10},
    {"nome": "Pro", "creditos": 200, "bonus": 30, "preco_centavos": 17990, "ordem": 20},
    {"nome": "Business", "creditos": 600, "bonus": 120, "preco_centavos": 49990, "ordem": 30},
    {"nome": "Enterprise", "creditos": 2000, "bonus": 500, "preco_centavos": 149990, "ordem": 40},
]


async def _seed_pacotes(db: AsyncSession) -> None:
    for p in PACOTES:
        existing = await db.scalar(select(PacoteCredito).where(PacoteCredito.nome == p["nome"]))
        if existing is None:
            db.add(
                PacoteCredito(
                    nome=p["nome"],
                    descricao=f'{p["creditos"]} créditos' + (f' + {p["bonus"]} bônus' if p["bonus"] else ""),
                    creditos=p["creditos"],
                    bonus=p["bonus"],
                    preco_centavos=p["preco_centavos"],
                    ordem=p["ordem"],
                    ativo=True,
                )
            )
    await db.flush()


# =============================================================================
# Superadmin inicial (Usuario + PerfilInterno)
# =============================================================================

async def _seed_superadmin(db: AsyncSession) -> None:
    email = settings.SUPERADMIN_EMAIL.lower()
    cpf = settings.SUPERADMIN_CPF
    u = await db.scalar(select(Usuario).where(Usuario.email == email))
    if u is None:
        u = Usuario(
            cpf=cpf,
            email=email,
            email_confirmado=True,
            senha_hash=hash_password(settings.SUPERADMIN_PASSWORD),
            nome_completo="Superadministrador PNR",
            telefone=None,
            ativo=True,
        )
        db.add(u)
        await db.flush()
        log.info("seed_superadmin_criado", email=email)
    else:
        log.info("seed_superadmin_ja_existe", email=email)

    perfil = await db.scalar(select(PerfilInterno).where(PerfilInterno.usuario_id == u.id))
    if perfil is None:
        db.add(
            PerfilInterno(
                usuario_id=u.id,
                tipo=PerfilInternoTipo.SUPERADMIN,
                ativo=True,
            )
        )
    await db.flush()


# =============================================================================
# Runner
# =============================================================================

async def run() -> None:
    async with SessionLocal() as db:
        try:
            log.info("seed_inicio")
            await _seed_categorias(db)
            log.info("seed_categorias_ok")
            await _seed_tipos_documento(db)
            log.info("seed_tipos_documento_ok")
            await _seed_planos(db)
            log.info("seed_planos_ok")
            await _seed_pacotes(db)
            log.info("seed_pacotes_ok")
            await _seed_superadmin(db)
            log.info("seed_superadmin_ok")
            await db.commit()
            log.info("seed_concluido")
        except Exception:
            await db.rollback()
            raise


def main() -> None:
    from app.core.logging import configure_logging

    configure_logging()
    asyncio.run(run())


if __name__ == "__main__":
    main()
