"""Seed inicial — execute com:

    docker compose exec backend python -m app.scripts.seed

Idempotente: roda múltiplas vezes sem duplicar (upsert por slug por nível).

Conteúdo seed:
  - Taxonomia do setor (3 níveis: Categoria → Subcategoria → TipoMaterial)
  - TiposDocumento padrão
  - Planos por Papel (gratuito + pago)
  - Pacotes de Crédito
  - Superadministrador
"""

from __future__ import annotations

import asyncio
import re
import unicodedata
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
    PapelTipo,
    PerfilInternoTipo,
)
from app.models.pacote_credito import PacoteCredito
from app.models.perfil_interno import PerfilInterno
from app.models.plano import Plano
from app.models.subcategoria import Subcategoria
from app.models.tipo_documento import TipoDocumento
from app.models.tipo_material import TipoMaterial
from app.models.usuario import Usuario

log = structlog.get_logger(__name__)


# =============================================================================
# Slugify
# =============================================================================

def _slug(text: str) -> str:
    """Slug ASCII em snake-kebab. 'Papelão ondulado' → 'papelao-ondulado'."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower().strip()
    # mantém alfanum e troca resto por '-'
    return re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")


# =============================================================================
# Taxonomia oficial do setor (validada pelo cliente)
#
# Estrutura:
#   {
#     "categoria": {nome, cor_hex, icone, ordem},
#     "subcategorias": [
#       {nome, regulada?, documentos?, tipos: [(nome, unidade_padrao), ...]},
#     ]
#   }
#
# Default de unidade_padrao = "kg" quando não especificado.
# =============================================================================

_DOCS_REGULADO_PADRAO = ["licenca_ambiental", "cadri"]
_DOCS_REGULADO_QUIMICO = ["licenca_ambiental", "cadri", "mtr"]


TAXONOMIA: list[dict] = [
    # ------------------------------------------------------------------ Papel
    {
        "categoria": {"nome": "Papel / Papelão", "cor_hex": "#3b82f6", "icone": "file-text", "ordem": 10},
        "subcategorias": [
            {"nome": "Papelão", "tipos": [
                "Papelão ondulado", "Papelão prensado",
            ]},
            {"nome": "Papel Branco", "tipos": [
                "Papel branco", "Papel sulfite", "Papel couchê",
            ]},
            {"nome": "Papel Misto", "tipos": [
                "Papel misto", "Aparas de papel", "Papel contaminado",
            ]},
            {"nome": "Papel Especial", "tipos": [
                "Papel arquivo", "Jornal", "Revista", "Lista telefônica", "Papel kraft",
                "Saco de cimento kraft", "Papel térmico", "Papel plastificado",
            ]},
            {"nome": "Embalagem Papel", "tipos": [
                "Tetra Pak",
            ]},
        ],
    },
    # ------------------------------------------------------------------ Plásticos
    {
        "categoria": {"nome": "Plásticos", "cor_hex": "#dc2626", "icone": "box", "ordem": 20},
        "subcategorias": [
            {"nome": "PET", "tipos": [
                "PET branca", "PET verde", "PET azul", "PET óleo", "PET colorida",
                "PET âmbar", "PET cristal", "PET prensada", "PET moída",
                "Fita PET verde", "Fita PET azul",
            ]},
            {"nome": "PEAD / PEBD / PE", "tipos": [
                "PEAD branco", "PEAD colorido", "PEAD sopro", "PEAD injeção",
                "PE branco leitoso", "PE colorido", "PE grosso (bombona)", "PE cristal",
                "PEBD filme", "Filme cristal", "Filme colorido", "Filme lona preta",
                "Filme agrícola", "Filme misturado", "Sacola cristal", "Sacola colorida",
                "Sacola preta", "Sacola mista", "Stretch", "Shrink",
            ]},
            {"nome": "PP", "tipos": [
                "PP mineral", "PP branco", "PP preto", "PP colorido", "PP margarina",
                "PP para-choque", "PP balde", "PP bacia", "PP tampinha", "PP cadeira",
                "PP copinho", "PP misto", "PP moído", "PP com carga mineral",
            ]},
            {"nome": "PVC", "tipos": [
                "PVC rígido", "PVC flexível", "PVC prensado", "PVC solto",
                "PVC mangueira", "PVC tubo", "PVC esquadria", "PVC cabo elétrico",
            ]},
            {"nome": "Outros Plásticos", "tipos": [
                "PS cristal", "PS copinho", "ABS", "Acrílico", "Nylon", "Policarbonato",
                "EVA", "PU", "Isopor / EPS", "Borracha", "Silicone", "Ráfia", "Big Bag",
                "Mangueira", "Caixa plástica", "Balde plástico", "Bombona", "Galão plástico",
            ]},
        ],
    },
    # ------------------------------------------------------------------ Metais
    {
        "categoria": {"nome": "Metais", "cor_hex": "#5c5a52", "icone": "wrench", "ordem": 30},
        "subcategorias": [
            {"nome": "Ferrosos", "tipos": [
                "Ferro misto", "Ferro fundido", "Sucata miúda", "Sucata graúda", "Aço",
                "Cavaco de ferro", "Chaparia", "Perfil metálico", "Estrutura metálica",
                "Lata de aço", "Tambor metálico", "Trilho", "Vergalhão",
            ]},
            {"nome": "Não Ferrosos", "tipos": [
                "Alumínio latinha", "Alumínio perfil", "Alumínio bloco", "Alumínio panela",
                "Alumínio chapa", "Alumínio duro", "Alumínio mole", "Cobre mel",
                "Cobre misto", "Cobre queimado", "Cobre estanhado", "Latão", "Bronze",
                "Zamac", "Chumbo", "Zinco", "Níquel", "Estanho", "Inox", "Metal misto",
                "Fios elétricos",
            ]},
        ],
    },
    # ------------------------------------------------------------------ Vidros
    {
        "categoria": {"nome": "Vidros", "cor_hex": "#10b981", "icone": "wine", "ordem": 40},
        "subcategorias": [
            {"nome": "Vidro Comum", "tipos": [
                "Vidro transparente", "Vidro verde", "Vidro âmbar", "Vidro misto",
                "Garrafa retornável", "Caco de vidro", "Vidro moído",
            ]},
            {"nome": "Vidro Especial", "tipos": [
                "Vidro temperado", "Vidro laminado", "Para-brisa",
            ]},
        ],
    },
    # ------------------------------------------------------------------ Óleos e Líquidos
    {
        "categoria": {"nome": "Óleos e Líquidos", "cor_hex": "#f59e0b", "icone": "droplet", "ordem": 50},
        "subcategorias": [
            {"nome": "Óleos Vegetais", "tipos_unidade": [
                ("Óleo vegetal usado", "l"),
            ]},
            {"nome": "Óleos Minerais e Industriais", "tipos_unidade": [
                ("Óleo mineral usado", "l"), ("Óleo hidráulico", "l"),
                ("Óleo lubrificante", "l"), ("Fluido industrial", "l"),
                ("Diesel contaminado", "l"), ("Querosene", "l"),
                ("Solvente usado", "l"), ("Tinta residual", "l"),
                ("Graxa", "kg"), ("Gordura industrial", "kg"),
            ]},
        ],
    },
    # ------------------------------------------------------------------ Eletrônicos / E-lixo
    {
        "categoria": {"nome": "Eletrônicos / E-lixo", "cor_hex": "#8b5cf6", "icone": "cpu", "ordem": 60},
        "subcategorias": [
            {"nome": "Equipamentos", "tipos_unidade": [
                ("Computadores", "unidade"), ("Notebooks", "unidade"),
                ("Celulares", "unidade"), ("Tablets", "unidade"),
                ("Monitores", "unidade"), ("TVs", "unidade"),
                ("Impressoras", "unidade"), ("Nobreaks", "unidade"),
                ("Equipamentos de rede", "unidade"), ("Eletrodomésticos", "unidade"),
            ]},
            {"nome": "Componentes", "tipos": [
                "Placas eletrônicas", "Fontes", "Cabos", "HDs", "Baterias",
            ]},
            {"nome": "Sucata Eletrônica", "tipos": [
                "Sucata eletrônica mista",
            ]},
        ],
    },
    # ------------------------------------------------------------------ Baterias / Pilhas
    {
        "categoria": {"nome": "Baterias / Pilhas", "cor_hex": "#facc15", "icone": "battery", "ordem": 70},
        "subcategorias": [
            {"nome": "Baterias", "tipos_unidade": [
                ("Bateria automotiva", "unidade"),
                ("Bateria estacionária", "unidade"),
                ("Bateria de celular", "unidade"),
                ("Nobreak", "unidade"),
            ]},
            {"nome": "Pilhas", "tipos": [
                "Pilhas alcalinas", "Pilhas recarregáveis", "Lítio",
            ]},
        ],
    },
    # ------------------------------------------------------------------ Madeira
    {
        "categoria": {"nome": "Madeira", "cor_hex": "#a16207", "icone": "tree-pine", "ordem": 80},
        "subcategorias": [
            {"nome": "Madeira Limpa", "tipos_unidade": [
                ("Madeira limpa", "m3"), ("Pallets", "unidade"),
                ("Compensado", "m3"), ("Serragem", "kg"),
                ("Cavaco de madeira", "m3"), ("Lenha reciclável", "m3"),
            ]},
            {"nome": "Madeira Contaminada", "tipos_unidade": [
                ("Madeira contaminada", "m3"), ("MDF", "m3"),
            ]},
        ],
    },
    # ------------------------------------------------------------------ Têxteis
    {
        "categoria": {"nome": "Têxteis", "cor_hex": "#ec4899", "icone": "shirt", "ordem": 90},
        "subcategorias": [
            {"nome": "Tecidos", "tipos": [
                "Retalho", "Roupa usada", "Jeans", "Algodão",
                "Poliéster", "TNT", "Tecido industrial",
            ]},
            {"nome": "Outros Têxteis", "tipos": [
                "Espuma", "Couro",
            ]},
        ],
    },
    # ------------------------------------------------------------------ Borracha / Pneus
    {
        "categoria": {"nome": "Borracha / Pneus", "cor_hex": "#1f2937", "icone": "circle", "ordem": 100},
        "subcategorias": [
            {"nome": "Pneus", "tipos_unidade": [
                ("Pneus", "unidade"), ("Câmara de ar", "unidade"),
            ]},
            {"nome": "Borracha Industrial", "tipos": [
                "Borracha industrial", "Correia", "EVA", "Silicone industrial",
            ]},
        ],
    },
    # ------------------------------------------------------------------ Resíduos Orgânicos
    {
        "categoria": {"nome": "Resíduos Orgânicos", "cor_hex": "#22c55e", "icone": "leaf", "ordem": 110},
        "subcategorias": [
            {"nome": "Orgânicos Alimentares", "tipos_unidade": [
                ("Restos alimentares", "kg"), ("Resíduo agrícola", "kg"),
                ("Compostagem", "kg"), ("Esterco", "kg"),
            ]},
            {"nome": "Orgânicos Vegetais", "tipos_unidade": [
                ("Poda", "m3"), ("Madeira orgânica", "m3"),
            ]},
        ],
    },
    # ------------------------------------------------------------------ Resíduos Industriais
    {
        "categoria": {"nome": "Resíduos Industriais", "cor_hex": "#7c3aed", "icone": "factory", "ordem": 120},
        "subcategorias": [
            {"nome": "Resíduos de Processo", "tipos": [
                "Borra industrial", "Lodo industrial", "Cinzas", "Escória",
            ]},
            {"nome": "Resíduos Contaminados", "tipos": [
                "Rejeito químico", "Resíduo contaminado", "Embalagem contaminada",
            ]},
        ],
    },
    # ------------------------------------------------------------------ Resíduos Hospitalares (REGULADO)
    {
        "categoria": {"nome": "Resíduos Hospitalares / Médicos", "cor_hex": "#dc2626", "icone": "alert-triangle", "ordem": 130},
        "subcategorias": [
            {
                "nome": "Infectantes",
                "regulada": True,
                "documentos": _DOCS_REGULADO_PADRAO,
                "tipos": [
                    "Perfurocortantes", "Seringas", "Luvas", "Máscaras",
                    "Material contaminado", "Resíduo biológico", "Resíduo infectante",
                ],
            },
            {
                "nome": "Químicos Hospitalares",
                "regulada": True,
                "documentos": _DOCS_REGULADO_PADRAO,
                "tipos": [
                    "Medicamentos vencidos", "Resíduo químico hospitalar",
                ],
            },
        ],
    },
    # ------------------------------------------------------------------ Construção Civil
    {
        "categoria": {"nome": "Construção Civil", "cor_hex": "#6b7280", "icone": "hammer", "ordem": 140},
        "subcategorias": [
            {"nome": "Entulho", "tipos_unidade": [
                ("Entulho", "m3"), ("Concreto", "m3"), ("Tijolo", "m3"),
                ("Cerâmica", "m3"), ("Gesso", "kg"), ("Areia contaminada", "m3"),
                ("Telha", "m3"), ("Cano PVC", "kg"), ("Madeira de obra", "m3"),
            ]},
        ],
    },
    # ------------------------------------------------------------------ Automotivo
    {
        "categoria": {"nome": "Automotivo", "cor_hex": "#0ea5e9", "icone": "car", "ordem": 150},
        "subcategorias": [
            {"nome": "Peças Automotivas", "tipos_unidade": [
                ("Radiador", "unidade"), ("Catalisador", "unidade"),
                ("Bateria automotiva", "unidade"), ("Para-choque", "unidade"),
                ("Vidro automotivo", "unidade"), ("Chicote elétrico", "kg"),
                ("Pneu", "unidade"), ("Peças metálicas", "kg"),
            ]},
            {"nome": "Fluidos Automotivos", "tipos_unidade": [
                ("Óleo usado", "l"),
            ]},
        ],
    },
    # ------------------------------------------------------------------ Químicos (REGULADO)
    {
        "categoria": {"nome": "Químicos", "cor_hex": "#7f1d1d", "icone": "flask-conical", "ordem": 160},
        "subcategorias": [
            {
                "nome": "Solventes e Ácidos",
                "regulada": True,
                "documentos": _DOCS_REGULADO_QUIMICO,
                "tipos_unidade": [
                    ("Solventes", "l"), ("Ácidos", "l"), ("Bases químicas", "l"),
                ],
            },
            {
                "nome": "Outros Químicos",
                "regulada": True,
                "documentos": _DOCS_REGULADO_QUIMICO,
                "tipos_unidade": [
                    ("Resinas", "kg"), ("Catalisadores", "kg"),
                    ("Tintas", "l"), ("Vernizes", "l"), ("Cola industrial", "kg"),
                ],
            },
        ],
    },
    # ------------------------------------------------------------------ Outros Recicláveis
    {
        "categoria": {"nome": "Outros Recicláveis", "cor_hex": "#06b6d4", "icone": "package", "ordem": 170},
        "subcategorias": [
            {"nome": "Embalagens Especiais", "tipos": [
                "Caixa de leite", "Embalagem longa vida", "Isopor",
                "Cápsula de café", "Embalagem aluminizada", "Embalagem flexível",
            ]},
            {"nome": "Material Processado", "tipos": [
                "Material prensado", "Material moído", "Material separado por cor",
                "Material separado por tipo",
            ]},
            {"nome": "Resíduo Geral", "tipos": [
                "Resíduo misto", "Material limpo", "Material contaminado",
            ]},
        ],
    },
]


def _iter_tipos(sub_def: dict) -> Iterable[tuple[str, str]]:
    """Normaliza 'tipos' (lista de nomes) e 'tipos_unidade' (lista de (nome, un))."""
    for nome in sub_def.get("tipos", []) or []:
        yield nome, "kg"
    for nome, unidade in sub_def.get("tipos_unidade", []) or []:
        yield nome, unidade


async def _seed_categorias(db: AsyncSession) -> None:
    """Popula categoria + subcategoria + tipo_material idempotentemente.

    Cada nível faz upsert por slug. Re-runs não duplicam.
    """
    for cat_def in TAXONOMIA:
        cdata = cat_def["categoria"]
        cat_slug = _slug(cdata["nome"])

        cat = await db.scalar(select(Categoria).where(Categoria.slug == cat_slug))
        if cat is None:
            cat = Categoria(
                nome=cdata["nome"],
                slug=cat_slug,
                cor_hex=cdata["cor_hex"],
                icone=cdata["icone"],
                ordem=cdata["ordem"],
                ativo=True,
            )
            db.add(cat)
            await db.flush()

        for sub_idx, sub_def in enumerate(cat_def["subcategorias"]):
            sub_slug = _slug(sub_def["nome"])
            sub = await db.scalar(
                select(Subcategoria).where(
                    Subcategoria.categoria_id == cat.id,
                    Subcategoria.slug == sub_slug,
                )
            )
            if sub is None:
                sub = Subcategoria(
                    categoria_id=cat.id,
                    nome=sub_def["nome"],
                    slug=sub_slug,
                    requer_validacao_documental=bool(sub_def.get("regulada", False)),
                    documentos_exigidos=list(sub_def.get("documentos", []) or []),
                    ordem=10 * (sub_idx + 1),
                    ativo=True,
                )
                db.add(sub)
                await db.flush()

            for tipo_idx, (tipo_nome, unidade) in enumerate(_iter_tipos(sub_def)):
                tipo_slug = _slug(tipo_nome)
                existing = await db.scalar(
                    select(TipoMaterial).where(
                        TipoMaterial.subcategoria_id == sub.id,
                        TipoMaterial.slug == tipo_slug,
                    )
                )
                if existing is None:
                    db.add(
                        TipoMaterial(
                            subcategoria_id=sub.id,
                            nome=tipo_nome,
                            slug=tipo_slug,
                            unidade_padrao=unidade,
                            atributos_especificos={},
                            ordem=10 * (tipo_idx + 1),
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
# Planos por Papel
# =============================================================================

def _planos_padrao() -> Iterable[dict]:
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
# Superadmin inicial
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
