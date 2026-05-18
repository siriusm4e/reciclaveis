"""Seed de demonstração — 5 perfis interconectados para apresentar o app a clientes.

    docker compose exec backend python -m app.scripts.seed_demo

Cria (idempotente):
  - 5 contas (catador PF, comprador PJ, gestor PJ, freteiro PJ, prefeitura SP)
  - Cada conta com Membro admin + Papel ativo + Preferência padrão
  - Estabelecimentos para as PJs (3)
  - Documentos APROVADOS para liberar fluxos regulados (8)
  - 4 Anúncios de venda do catador (PET, latinha, papelão, vidro) — espalhados em SP
  - 2 Ofertas de compra do comprador (PET com Alerta Pago ativo + papelão)
  - 1 Anúncio de máquina (prensa) e 1 de serviço (gestão hospitalar)
  - 1 Anúncio de frete do freteiro (truck 5t)
  - 1 Negociação em andamento + 4 mensagens (catador ↔ comprador)
  - 1 Negociação concluída + avaliação 5★ visível
  - 50 créditos para o comprador (compra) + boost ativo na oferta de PET
  - 2 Pedidos de coleta pública (cidadãos para prefeitura SP)
  - 1 Campanha publicada
  - 1 Conteúdo educativo

Requer: alembic upgrade head + seed básico já executados.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.anuncio_frete import AnuncioFrete
from app.models.anuncio_maquina import AnuncioMaquina
from app.models.anuncio_servico import AnuncioServico
from app.models.anuncio_venda import AnuncioVenda
from app.models.avaliacao import Avaliacao
from app.models.campanha_publica import CampanhaPublica
from app.models.categoria import Categoria
from app.models.conta import Conta
from app.models.conteudo_educativo import ConteudoEducativo
from app.models.documento import Documento
from app.models.enums import (
    AnuncioStatus,
    AnuncioVendaStatus,
    CampanhaStatus,
    CondicaoEquipamento,
    CondicaoForma,
    CondicaoLimpeza,
    CondicaoUmidade,
    ConteudoTipo,
    ContaStatus,
    ContaTipo,
    DocumentoStatus,
    FrequenciaAnuncio,
    MensagemTipo,
    ModalidadeMaquina,
    NegociacaoStatus,
    OfertaCompraStatus,
    PapelInternoMembro,
    PapelStatus,
    PapelTipo,
    PedidoColetaStatus,
    PublicacaoTipo,
    TransacaoTipo,
    UnidadeCobrancaServico,
)
from app.models.estabelecimento import Estabelecimento
from app.models.membro import Membro
from app.models.mensagem import Mensagem
from app.models.negociacao import Negociacao
from app.models.oferta_compra import OfertaCompra
from app.models.papel import PapelAtivado
from app.models.pedido_coleta_publica import PedidoColetaPublica
from app.models.preferencia_comunicacao import PreferenciaComunicacao
from app.models.tipo_documento import TipoDocumento
from app.models.tipo_material import TipoMaterial
from app.models.transacao_credito import TransacaoCredito
from app.models.usuario import Usuario
from app.utils.geo import aplicar_offset_privacidade, make_point_wkt

log = structlog.get_logger(__name__)


# =============================================================================
# Coordenadas reais em Curitiba/PR e Região Metropolitana
# Compradores ficam <= 15km do catador para que tudo apareça em buscas locais
# =============================================================================

# Catador: Centro de Curitiba (Praça Tiradentes / Rua XV de Novembro)
COORDS_CATADOR = (-25.4296, -49.2719)

# Anúncios do catador espalhados em bairros de Curitiba
COORDS_PET = (-25.4360, -49.2920)         # Batel — Av. do Batel
COORDS_LATINHA = (-25.4480, -49.2880)     # Água Verde — Av. República Argentina
COORDS_PAPELAO = (-25.5046, -49.2570)     # Boqueirão — Av. Marechal Floriano Peixoto
COORDS_VIDRO = (-25.4145, -49.2407)       # Bairro Alto — Av. Paraná

# Comprador: Cidade Industrial de Curitiba (CIC), ~10km do catador
COORDS_COMPRADOR = (-25.4855, -49.3380)

# Gestor: São José dos Pinhais (RMC), ~14km do catador
COORDS_GESTOR = (-25.5354, -49.2058)

# Freteiro: Pinhais (RMC), ~8km do catador
COORDS_FRETEIRO = (-25.4456, -49.1924)

# Pedidos cidadãos em Curitiba
COORDS_PEDIDO_1 = (-25.4087, -49.2747)    # Ahú — Av. Anita Garibaldi
COORDS_PEDIDO_2 = (-25.4533, -49.2364)    # Jardim das Américas — próx. UFPR


# =============================================================================
# Helpers
# =============================================================================

async def _get_or_create_usuario(
    db: AsyncSession, *, cpf: str, email: str, senha: str, nome: str, telefone: Optional[str]
) -> Usuario:
    u = await db.scalar(select(Usuario).where(Usuario.email == email))
    if u:
        return u
    u = Usuario(
        cpf=cpf,
        email=email,
        email_confirmado=True,
        senha_hash=hash_password(senha),
        nome_completo=nome,
        telefone=telefone,
        ativo=True,
    )
    db.add(u)
    await db.flush()
    return u


async def _get_or_create_conta(
    db: AsyncSession,
    *,
    usuario: Usuario,
    tipo: ContaTipo,
    nome_publico: str,
    cnpj: Optional[str] = None,
    escopo_territorial: Optional[dict] = None,
) -> Conta:
    # Se já existe Membro do usuário em uma Conta do mesmo tipo, reusa
    existing_id = await db.scalar(
        select(Conta.id)
        .join(Membro, Membro.conta_id == Conta.id)
        .where(Membro.usuario_id == usuario.id, Conta.tipo == tipo)
        .limit(1)
    )
    if existing_id:
        c = await db.scalar(select(Conta).where(Conta.id == existing_id))
        if c:
            return c

    c = Conta(
        tipo=tipo,
        status=ContaStatus.ATIVA,  # Seed demo ativa diretamente
        nome_publico=nome_publico,
        cnpj=cnpj,
        escopo_territorial=escopo_territorial,
        cortesia_ativa=False,
    )
    db.add(c)
    await db.flush()

    db.add(
        Membro(usuario_id=usuario.id, conta_id=c.id, papel_interno=PapelInternoMembro.ADMIN)
    )
    db.add(PreferenciaComunicacao(conta_id=c.id))
    await db.flush()
    return c


async def _get_or_create_papel(
    db: AsyncSession, *, conta: Conta, papel: PapelTipo
) -> PapelAtivado:
    p = await db.scalar(
        select(PapelAtivado).where(PapelAtivado.conta_id == conta.id, PapelAtivado.papel == papel)
    )
    if p:
        if p.status != PapelStatus.ATIVO:
            p.status = PapelStatus.ATIVO
            await db.flush()
        return p
    p = PapelAtivado(
        conta_id=conta.id, papel=papel, status=PapelStatus.ATIVO, dados_complementares={}
    )
    db.add(p)
    await db.flush()
    return p


async def _get_or_create_estabelecimento(
    db: AsyncSession,
    *,
    conta: Conta,
    nome: str,
    cep: str,
    logradouro: str,
    numero: str,
    bairro: str,
    cidade: str,
    uf: str,
    ibge: str,
    lat: float,
    lng: float,
) -> Estabelecimento:
    e = await db.scalar(
        select(Estabelecimento).where(
            Estabelecimento.conta_id == conta.id, Estabelecimento.nome == nome
        )
    )
    if e:
        return e
    e = Estabelecimento(
        conta_id=conta.id,
        nome=nome,
        cep=cep,
        logradouro=logradouro,
        numero=numero,
        bairro=bairro,
        cidade=cidade,
        uf=uf,
        ibge_municipio=ibge,
        geom=make_point_wkt(lat, lng),
    )
    db.add(e)
    await db.flush()
    return e


async def _aprovar_documento(
    db: AsyncSession,
    *,
    conta: Conta,
    tipo_slug: str,
    estabelecimento_id: Optional[UUID] = None,
    aprovado_por_id: Optional[UUID] = None,
    vencimento_dias: Optional[int] = 365,
) -> Optional[Documento]:
    tipo = await db.scalar(select(TipoDocumento).where(TipoDocumento.slug == tipo_slug))
    if tipo is None:
        log.warning("seed_demo_tipo_doc_ausente", slug=tipo_slug)
        return None

    existing = await db.scalar(
        select(Documento).where(
            Documento.conta_id == conta.id,
            Documento.tipo_documento_id == tipo.id,
            Documento.status == DocumentoStatus.APROVADO,
        )
    )
    if existing:
        return existing

    venc = None
    if tipo.tem_vencimento and vencimento_dias:
        venc = (datetime.now(tz=timezone.utc) + timedelta(days=vencimento_dias)).date()

    doc = Documento(
        conta_id=conta.id,
        estabelecimento_id=estabelecimento_id,
        tipo_documento_id=tipo.id,
        numero=f"DEMO-{tipo.slug.upper()}-001",
        data_emissao=(datetime.now(tz=timezone.utc) - timedelta(days=30)).date(),
        data_vencimento=venc,
        arquivo_path=f"demo/seed_{tipo.slug}.pdf",
        mime="application/pdf",
        tamanho_bytes=12345,
        status=DocumentoStatus.APROVADO,
        aprovado_por_admin_id=aprovado_por_id,
    )
    db.add(doc)
    await db.flush()
    return doc


async def _tipo_material_por_slug(db: AsyncSession, slug: str) -> Optional[TipoMaterial]:
    """Busca TipoMaterial pelo slug (unique apenas dentro de subcategoria;
    no seed demo cada slug abaixo é único globalmente)."""
    return await db.scalar(select(TipoMaterial).where(TipoMaterial.slug == slug))


# =============================================================================
# Personagens
# =============================================================================

async def seed_catador(db: AsyncSession) -> tuple[Usuario, Conta, PapelAtivado]:
    u = await _get_or_create_usuario(
        db,
        cpf="11111111111",
        email="catador@pnr.com.br",
        senha="catador123!",
        nome="João Catador",
        telefone="11987650001",
    )
    c = await _get_or_create_conta(
        db, usuario=u, tipo=ContaTipo.PF, nome_publico="João Catador"
    )
    p = await _get_or_create_papel(db, conta=c, papel=PapelTipo.CATADOR)
    await _aprovar_documento(db, conta=c, tipo_slug="selfie_documento", vencimento_dias=None)
    return u, c, p


async def seed_comprador(db: AsyncSession) -> tuple[Usuario, Conta, PapelAtivado, Estabelecimento]:
    u = await _get_or_create_usuario(
        db,
        cpf="22222222222",
        email="comprador@pnr.com.br",
        senha="comprador123!",
        nome="Maria Comprado",
        telefone="11987650002",
    )
    c = await _get_or_create_conta(
        db,
        usuario=u,
        tipo=ContaTipo.PJ_PRIVADA,
        nome_publico="Recicladora Verde Vale Ltda",
        cnpj="11222333000181",  # CNPJ válido (dígitos corretos)
    )
    p = await _get_or_create_papel(db, conta=c, papel=PapelTipo.COMPRADOR)
    est = await _get_or_create_estabelecimento(
        db,
        conta=c,
        nome="Galpão CIC Curitiba",
        cep="81460020",
        logradouro="Av. Juscelino K. de Oliveira",
        numero="11500",
        bairro="Cidade Industrial",
        cidade="Curitiba",
        uf="PR",
        ibge="4106902",
        lat=COORDS_COMPRADOR[0],
        lng=COORDS_COMPRADOR[1],
    )
    # Documentos aprovados — comprador pleno (pode atuar até em regulados)
    for slug in ("cnpj_ativo", "contrato_social", "alvara_funcionamento"):
        await _aprovar_documento(db, conta=c, tipo_slug=slug)
    for slug in ("licenca_ambiental", "cadri"):
        await _aprovar_documento(
            db, conta=c, tipo_slug=slug, estabelecimento_id=est.id, vencimento_dias=180
        )
    return u, c, p, est


async def seed_gestor(db: AsyncSession) -> tuple[Usuario, Conta, PapelAtivado, Estabelecimento]:
    u = await _get_or_create_usuario(
        db,
        cpf="33333333333",
        email="gestor@pnr.com.br",
        senha="gestor123!",
        nome="Carlos Gestor",
        telefone="11987650003",
    )
    c = await _get_or_create_conta(
        db,
        usuario=u,
        tipo=ContaTipo.PJ_PRIVADA,
        nome_publico="GreenOps Gestão de Resíduos S.A.",
        cnpj="44555666000122",
    )
    p = await _get_or_create_papel(db, conta=c, papel=PapelTipo.GESTOR_RESIDUOS)
    est = await _get_or_create_estabelecimento(
        db,
        conta=c,
        nome="Base São José dos Pinhais",
        cep="83005000",
        logradouro="Av. Rui Barbosa",
        numero="2500",
        bairro="Centro",
        cidade="São José dos Pinhais",
        uf="PR",
        ibge="4125506",
        lat=COORDS_GESTOR[0],
        lng=COORDS_GESTOR[1],
    )
    for slug in ("cnpj_ativo", "contrato_social"):
        await _aprovar_documento(db, conta=c, tipo_slug=slug)
    for slug in ("licenca_ambiental", "cadri"):
        await _aprovar_documento(
            db, conta=c, tipo_slug=slug, estabelecimento_id=est.id, vencimento_dias=200
        )
    return u, c, p, est


async def seed_freteiro(db: AsyncSession) -> tuple[Usuario, Conta, PapelAtivado, Estabelecimento]:
    u = await _get_or_create_usuario(
        db,
        cpf="44444444444",
        email="freteiro@pnr.com.br",
        senha="freteiro123!",
        nome="Pedro Logística",
        telefone="11987650004",
    )
    c = await _get_or_create_conta(
        db,
        usuario=u,
        tipo=ContaTipo.PJ_PRIVADA,
        nome_publico="Transportes ProFrete EIRELI",
        cnpj="77888999000155",
    )
    p = await _get_or_create_papel(db, conta=c, papel=PapelTipo.FRETEIRO)
    est = await _get_or_create_estabelecimento(
        db,
        conta=c,
        nome="Garagem Pinhais",
        cep="83323000",
        logradouro="Rod. João Leopoldo Jacomel",
        numero="14500",
        bairro="Jardim Pedro Demeterco",
        cidade="Pinhais",
        uf="PR",
        ibge="4119152",
        lat=COORDS_FRETEIRO[0],
        lng=COORDS_FRETEIRO[1],
    )
    for slug in ("cnpj_ativo", "antt", "mtr"):
        await _aprovar_documento(db, conta=c, tipo_slug=slug, vencimento_dias=300)
    return u, c, p, est


async def seed_prefeitura(db: AsyncSession) -> tuple[Usuario, Conta, PapelAtivado]:
    u = await _get_or_create_usuario(
        db,
        cpf="55555555555",
        email="prefeitura@pnr.com.br",
        senha="prefeitura123!",
        nome="Ana Servidora Pública",
        telefone="1133220005",
    )
    c = await _get_or_create_conta(
        db,
        usuario=u,
        tipo=ContaTipo.ORGAO_PUBLICO,
        nome_publico="Sec. Municipal do Meio Ambiente — Curitiba",
        cnpj="76105550000122",  # CNPJ exemplo Prefeitura Curitiba
        escopo_territorial={"escopo": "municipio", "uf": "PR", "ibge": "4106902"},
    )
    p = await _get_or_create_papel(db, conta=c, papel=PapelTipo.PREFEITURA)
    return u, c, p


# =============================================================================
# Publicações e relacionamentos
# =============================================================================

async def seed_anuncios_catador(
    db: AsyncSession, *, conta_catador: Conta, papel_catador: PapelAtivado
) -> dict[str, AnuncioVenda]:
    """4 anúncios de venda do catador, em locais diferentes de Curitiba."""
    # Slugs alinhados à taxonomia oficial (Bloco 2):
    #   Plásticos > PET > PET cristal
    #   Metais > Não Ferrosos > Alumínio latinha
    #   Papel/Papelão > Papelão > Papelão ondulado
    #   Vidros > Vidro Comum > Vidro transparente
    pet = await _tipo_material_por_slug(db, "pet-cristal")
    latinha = await _tipo_material_por_slug(db, "aluminio-latinha")
    papelao = await _tipo_material_por_slug(db, "papelao-ondulado")
    vidro = await _tipo_material_por_slug(db, "vidro-transparente")

    out: dict[str, AnuncioVenda] = {}
    if pet:
        out["pet"] = await _get_or_create_anuncio(
            db, conta=conta_catador, papel=papel_catador, tipo=pet,
            preco=Decimal("2.50"), volume=Decimal("50"),
            frequencia=FrequenciaAnuncio.RECORRENTE, intervalo="semanal",
            lat=COORDS_PET[0], lng=COORDS_PET[1],
            condicao_limpeza="limpo",
            condicao_umidade="seco",
            condicao_forma="prensado",
        )
    if latinha:
        out["latinha"] = await _get_or_create_anuncio(
            db, conta=conta_catador, papel=papel_catador, tipo=latinha,
            preco=Decimal("9.80"), volume=Decimal("30"),
            frequencia=FrequenciaAnuncio.LOTE_UNICO, intervalo=None,
            lat=COORDS_LATINHA[0], lng=COORDS_LATINHA[1],
            condicao_limpeza="limpo",
            condicao_umidade="seco",
            condicao_forma="fardo",
        )
    if papelao:
        out["papelao"] = await _get_or_create_anuncio(
            db, conta=conta_catador, papel=papel_catador, tipo=papelao,
            preco=Decimal("0.50"), volume=Decimal("100"),
            frequencia=FrequenciaAnuncio.LOTE_UNICO, intervalo=None,
            lat=COORDS_PAPELAO[0], lng=COORDS_PAPELAO[1],
            condicao_limpeza="limpo",
            condicao_umidade="seco",
            condicao_forma="fardo",
        )
    if vidro:
        out["vidro"] = await _get_or_create_anuncio(
            db, conta=conta_catador, papel=papel_catador, tipo=vidro,
            preco=Decimal("0.30"), volume=Decimal("80"),
            frequencia=FrequenciaAnuncio.RECORRENTE, intervalo="quinzenal",
            lat=COORDS_VIDRO[0], lng=COORDS_VIDRO[1],
            condicao_limpeza="limpo",
            condicao_umidade="seco",
            condicao_forma="solto",
        )
    return out


async def _get_or_create_anuncio(
    db: AsyncSession, *, conta: Conta, papel: PapelAtivado, tipo: TipoMaterial,
    preco: Decimal, volume: Decimal,
    frequencia: FrequenciaAnuncio, intervalo: Optional[str],
    lat: float, lng: float,
    condicao_limpeza: CondicaoLimpeza | None = None,
    condicao_umidade: CondicaoUmidade | None = None,
    condicao_forma: CondicaoForma | None = None,
) -> AnuncioVenda:
    # AnuncioVenda não tem mais titulo/descricao livre — lookup pelo
    # par (conta, tipo_material) é único no contexto demo.
    existing = await db.scalar(
        select(AnuncioVenda).where(
            AnuncioVenda.conta_id == conta.id,
            AnuncioVenda.tipo_material_id == tipo.id,
        )
    )
    if existing:
        return existing

    lat_pub, lng_pub, offset_m = aplicar_offset_privacidade(lat, lng, territorio="urbano")
    obj = AnuncioVenda(
        conta_id=conta.id,
        papel_id=papel.id,
        tipo_material_id=tipo.id,
        atributos={},
        condicao_limpeza=condicao_limpeza,
        condicao_umidade=condicao_umidade,
        condicao_forma=condicao_forma,
        lat_real=lat,
        lng_real=lng,
        lat_pub=lat_pub,
        lng_pub=lng_pub,
        offset_m=offset_m,
        geom_pub=make_point_wkt(lat_pub, lng_pub),
        territorio="urbano",
        preco_pretendido=preco,
        unidade=tipo.unidade_padrao,
        volume_estimado=volume,
        frequencia=frequencia,
        intervalo_geracao=intervalo,
        prazo_validade=datetime.now(tz=timezone.utc) + timedelta(days=45),
        status=AnuncioVendaStatus.PUBLICADO,
        fotos=[],
        aceita_alerta_pago_de_terceiros=True,
    )
    db.add(obj)
    await db.flush()
    return obj


async def seed_ofertas_comprador(
    db: AsyncSession, *, conta_comp: Conta, papel_comp: PapelAtivado
) -> dict[str, OfertaCompra]:
    pet = await _tipo_material_por_slug(db, "pet-cristal")
    papelao = await _tipo_material_por_slug(db, "papelao-ondulado")
    out: dict[str, OfertaCompra] = {}
    if pet:
        out["pet"] = await _get_or_create_oferta(
            db, conta=conta_comp, papel=papel_comp, tipo=pet,
            titulo="Compro PET cristal — pagamento à vista",
            descricao="Volume mínimo 30kg, busco fornecedores constantes.",
            preco=Decimal("3.20"), vol_min=Decimal("30"), vol_max=Decimal("500"),
            volume_minimo_kg=30.0,
            condicao_limpeza="limpo",
            condicao_umidade="seco",
            condicao_forma="prensado",
            raio_km=50, retira=True,
            lat=COORDS_COMPRADOR[0], lng=COORDS_COMPRADOR[1],
            boost_ativo=True,
        )
    if papelao:
        out["papelao"] = await _get_or_create_oferta(
            db, conta=conta_comp, papel=papel_comp, tipo=papelao,
            titulo="Compro papelão prensado",
            descricao="Coleto na sua sede acima de 200kg.",
            preco=Decimal("0.65"), vol_min=Decimal("200"), vol_max=None,
            volume_minimo_kg=200.0,
            condicao_limpeza="limpo",
            condicao_umidade="seco",
            condicao_forma="fardo",
            raio_km=80, retira=True,
            lat=COORDS_COMPRADOR[0], lng=COORDS_COMPRADOR[1],
            boost_ativo=False,
        )
    return out


async def _get_or_create_oferta(
    db: AsyncSession, *, conta: Conta, papel: PapelAtivado, tipo: TipoMaterial,
    titulo: str, descricao: str, preco: Decimal,
    vol_min: Decimal, vol_max: Optional[Decimal],
    volume_minimo_kg: Optional[float],
    condicao_limpeza: Optional[CondicaoLimpeza],
    condicao_umidade: Optional[CondicaoUmidade],
    condicao_forma: Optional[CondicaoForma],
    raio_km: int, retira: bool, lat: float, lng: float, boost_ativo: bool,
) -> OfertaCompra:
    existing = await db.scalar(
        select(OfertaCompra).where(
            OfertaCompra.conta_id == conta.id,
            OfertaCompra.tipo_material_id == tipo.id,
            OfertaCompra.titulo == titulo,
        )
    )
    if existing:
        return existing

    now = datetime.now(tz=timezone.utc)
    obj = OfertaCompra(
        conta_id=conta.id,
        papel_id=papel.id,
        tipo_material_id=tipo.id,
        titulo=titulo,
        descricao=descricao,
        especificacao={},
        preco_paga=preco,
        unidade=tipo.unidade_padrao,
        volume_min=vol_min,
        volume_max=vol_max,
        volume_minimo_kg=volume_minimo_kg,
        condicao_limpeza=condicao_limpeza,
        condicao_umidade=condicao_umidade,
        condicao_forma=condicao_forma,
        lat=lat,
        lng=lng,
        raio_km=raio_km,
        geom=make_point_wkt(lat, lng),
        retira=retira,
        prazo_validade=now + timedelta(days=60),
        status=OfertaCompraStatus.PUBLICADA,
        boost_ativo=boost_ativo,
        boost_raio_km=80 if boost_ativo else None,
        boost_duracao_horas=48 if boost_ativo else None,
        boost_inicio=now if boost_ativo else None,
        boost_fim=now + timedelta(hours=48) if boost_ativo else None,
        boost_segmentacao={},
        boost_auditoria={"cobertura": 6, "cobertura_minima": 3, "disparou": True, "ts": now.isoformat()} if boost_ativo else None,
    )
    db.add(obj)
    await db.flush()
    return obj


async def seed_negociacao_em_andamento(
    db: AsyncSession,
    *,
    anuncio_pet: AnuncioVenda,
    conta_catador: Conta,
    conta_comprador: Conta,
    usuario_catador: Usuario,
    usuario_comprador: Usuario,
) -> Negociacao:
    existing = await db.scalar(
        select(Negociacao).where(
            Negociacao.publicacao_id == anuncio_pet.id,
            Negociacao.publicacao_tipo == PublicacaoTipo.ANUNCIO_VENDA,
            Negociacao.conta_vendedora_id == conta_catador.id,
            Negociacao.conta_compradora_id == conta_comprador.id,
        )
    )
    if existing:
        return existing

    now = datetime.now(tz=timezone.utc)
    neg = Negociacao(
        publicacao_id=anuncio_pet.id,
        publicacao_tipo=PublicacaoTipo.ANUNCIO_VENDA,
        conta_vendedora_id=conta_catador.id,
        conta_compradora_id=conta_comprador.id,
        status=NegociacaoStatus.ABERTA,
        ultima_mensagem_em=now - timedelta(minutes=8),
        ultima_mensagem_preview="Posso buscar na sexta às 14h.",
        audit_trail=[{"transicao": "abertura", "ts": (now - timedelta(hours=2)).isoformat(), "conta_id": str(conta_comprador.id)}],
    )
    db.add(neg)
    await db.flush()

    mensagens = [
        (conta_comprador.id, usuario_comprador.id, "Olá! Tenho interesse no seu PET. Você consegue 50kg essa semana?", now - timedelta(hours=2)),
        (conta_catador.id, usuario_catador.id, "Olá! Sim, fechei agora 50kg. Já prensado em fardos de 5kg.", now - timedelta(hours=1, minutes=45)),
        (conta_comprador.id, usuario_comprador.id, "Perfeito. Pago R$ 3,00/kg, busco no seu local. Combinado?", now - timedelta(minutes=30)),
        (conta_catador.id, usuario_catador.id, "Posso buscar na sexta às 14h.", now - timedelta(minutes=8)),
    ]
    for conta_id, usuario_id, conteudo, ts in mensagens:
        m = Mensagem(
            negociacao_id=neg.id,
            conta_remetente_id=conta_id,
            usuario_remetente_id=usuario_id,
            conteudo=conteudo,
            tipo=MensagemTipo.TEXTO,
        )
        # Força created_at específico (passa do default)
        m.created_at = ts
        db.add(m)
    await db.flush()
    return neg


async def seed_negociacao_concluida_com_avaliacao(
    db: AsyncSession,
    *,
    anuncio_papelao: AnuncioVenda,
    conta_catador: Conta,
    conta_comprador: Conta,
) -> None:
    existing = await db.scalar(
        select(Negociacao).where(
            Negociacao.publicacao_id == anuncio_papelao.id,
            Negociacao.publicacao_tipo == PublicacaoTipo.ANUNCIO_VENDA,
            Negociacao.status == NegociacaoStatus.CONCLUIDA,
        )
    )
    if existing:
        return

    now = datetime.now(tz=timezone.utc)
    neg = Negociacao(
        publicacao_id=anuncio_papelao.id,
        publicacao_tipo=PublicacaoTipo.ANUNCIO_VENDA,
        conta_vendedora_id=conta_catador.id,
        conta_compradora_id=conta_comprador.id,
        status=NegociacaoStatus.CONCLUIDA,
        aceite_localizacao_exata_vendedor=True,
        aceite_localizacao_exata_comprador=True,
        combinada_em=now - timedelta(days=10),
        ultima_mensagem_em=now - timedelta(days=8),
        ultima_mensagem_preview="Obrigado pelo papelão, ótima qualidade!",
        audit_trail=[
            {"transicao": "abertura", "ts": (now - timedelta(days=12)).isoformat(), "conta_id": str(conta_comprador.id)},
            {"transicao": "combinada", "ts": (now - timedelta(days=10)).isoformat(), "conta_id": str(conta_catador.id)},
            {"transicao": "concluida", "ts": (now - timedelta(days=8)).isoformat(), "conta_id": str(conta_comprador.id)},
        ],
    )
    db.add(neg)
    await db.flush()

    # Avaliações recíprocas → ambas visíveis
    db.add(
        Avaliacao(
            negociacao_id=neg.id,
            avaliador_conta_id=conta_comprador.id,
            avaliado_conta_id=conta_catador.id,
            papel_avaliado=PapelTipo.CATADOR,
            nota=5,
            subnotas={"pontualidade": 5, "qualidade": 5},
            comentario="Excelente catador, material prensado e pesado certinho.",
            visivel=True,
        )
    )
    db.add(
        Avaliacao(
            negociacao_id=neg.id,
            avaliador_conta_id=conta_catador.id,
            avaliado_conta_id=conta_comprador.id,
            papel_avaliado=PapelTipo.COMPRADOR,
            nota=5,
            subnotas={"comunicacao": 5, "pagamento": 5},
            comentario="Pagamento à vista, retirada no horário combinado.",
            visivel=True,
        )
    )
    await db.flush()


async def seed_creditos_comprador(db: AsyncSession, *, conta_comp: Conta) -> None:
    existing = await db.scalar(
        select(TransacaoCredito).where(
            TransacaoCredito.conta_id == conta_comp.id, TransacaoCredito.tipo == TransacaoTipo.COMPRA
        )
    )
    if existing:
        return
    db.add(
        TransacaoCredito(
            conta_id=conta_comp.id,
            tipo=TransacaoTipo.COMPRA,
            valor=200,
            descricao="Compra de pacote Pro (demo)",
            referencia_tipo="pacote_credito",
        )
    )
    db.add(
        TransacaoCredito(
            conta_id=conta_comp.id,
            tipo=TransacaoTipo.CONSUMO,
            valor=-10,
            descricao="Alerta Pago para oferta PET",
            referencia_tipo="oferta_compra",
        )
    )
    await db.flush()


async def seed_anuncio_servico_gestor(
    db: AsyncSession, *, conta_gestor: Conta, papel_gestor: PapelAtivado
) -> None:
    existing = await db.scalar(
        select(AnuncioServico).where(
            AnuncioServico.conta_id == conta_gestor.id,
            AnuncioServico.tipo_servico == "Gestão completa de resíduos hospitalares",
        )
    )
    if existing:
        return
    db.add(
        AnuncioServico(
            conta_id=conta_gestor.id,
            papel_id=papel_gestor.id,
            tipo_servico="Gestão completa de resíduos hospitalares",
            descricao="Coleta, transporte, tratamento e destinação final para Grupo A e E. Emitimos MTR e CADRI.",
            raio_operacional_km=120,
            unidade_cobranca=UnidadeCobrancaServico.VISITA,
            preco=Decimal("450.00"),
            requer_visita_tecnica=True,
            disponibilidade={"dias": ["seg", "ter", "qua", "qui", "sex"]},
            lat=COORDS_GESTOR[0],
            lng=COORDS_GESTOR[1],
            geom=make_point_wkt(COORDS_GESTOR[0], COORDS_GESTOR[1]),
            prazo_validade=datetime.now(tz=timezone.utc) + timedelta(days=120),
            status=AnuncioStatus.PUBLICADO,
        )
    )
    await db.flush()


async def seed_anuncio_maquina(
    db: AsyncSession, *, conta_gestor: Conta, papel_gestor: PapelAtivado
) -> None:
    existing = await db.scalar(
        select(AnuncioMaquina).where(
            AnuncioMaquina.conta_id == conta_gestor.id,
            AnuncioMaquina.modelo == "PV-150",
        )
    )
    if existing:
        return
    db.add(
        AnuncioMaquina(
            conta_id=conta_gestor.id,
            papel_id=papel_gestor.id,
            categoria_equipamento="Prensa hidráulica",
            marca="EcoMáquinas",
            modelo="PV-150",
            ano=2022,
            capacidade="150 ton",
            tensao="380V trifásico",
            descricao="Prensa vertical seminova, manutenção em dia. Ideal para PET, papelão, PEAD.",
            condicao=CondicaoEquipamento.SEMINOVO,
            modalidade=ModalidadeMaquina.VENDA,
            aceita_visita_tecnica=True,
            preco=Decimal("38000.00"),
            documentacao_disponivel=True,
            fotos=[],
            lat=COORDS_GESTOR[0],
            lng=COORDS_GESTOR[1],
            geom=make_point_wkt(COORDS_GESTOR[0], COORDS_GESTOR[1]),
            prazo_validade=datetime.now(tz=timezone.utc) + timedelta(days=90),
            status=AnuncioStatus.PUBLICADO,
        )
    )
    await db.flush()


async def seed_anuncio_frete(
    db: AsyncSession, *, conta_freteiro: Conta, papel_freteiro: PapelAtivado
) -> None:
    existing = await db.scalar(
        select(AnuncioFrete).where(
            AnuncioFrete.conta_id == conta_freteiro.id,
            AnuncioFrete.tipo_veiculo == "Truck",
        )
    )
    if existing:
        return
    db.add(
        AnuncioFrete(
            conta_id=conta_freteiro.id,
            papel_id=papel_freteiro.id,
            tipo_veiculo="Truck",
            capacidade_t=Decimal("5.0"),
            capacidade_m3=Decimal("25.0"),
            tara=Decimal("6.5"),
            raio_operacional_km=300,
            categorias_residuo_aceitas=["metais", "plasticos", "papeis", "vidros"],
            licencas=["antt", "mtr"],
            emite_nf=True,
            lat=COORDS_FRETEIRO[0],
            lng=COORDS_FRETEIRO[1],
            geom=make_point_wkt(COORDS_FRETEIRO[0], COORDS_FRETEIRO[1]),
            prazo_validade=datetime.now(tz=timezone.utc) + timedelta(days=180),
            status=AnuncioStatus.PUBLICADO,
        )
    )
    await db.flush()


async def seed_pedidos_coleta_publica(
    db: AsyncSession, *, conta_solicitante: Conta, conta_prefeitura: Conta
) -> None:
    pedidos = [
        {
            "bairro": "Ahú",
            "tipo": "Entulho de construção doméstica",
            "lat": COORDS_PEDIDO_1[0],
            "lng": COORDS_PEDIDO_1[1],
            "descricao": "Restos de reforma de banheiro — cerca de 1m³",
            "status": PedidoColetaStatus.TRIADA,
        },
        {
            "bairro": "Jardim das Américas",
            "tipo": "Móveis e colchão",
            "lat": COORDS_PEDIDO_2[0],
            "lng": COORDS_PEDIDO_2[1],
            "descricao": "1 sofá 3 lugares + colchão queen",
            "status": PedidoColetaStatus.AGENDADA,
        },
    ]
    for p in pedidos:
        existing = await db.scalar(
            select(PedidoColetaPublica).where(
                PedidoColetaPublica.conta_solicitante_id == conta_solicitante.id,
                PedidoColetaPublica.bairro == p["bairro"],
                PedidoColetaPublica.tipo_residuo == p["tipo"],
            )
        )
        if existing:
            continue
        db.add(
            PedidoColetaPublica(
                conta_solicitante_id=conta_solicitante.id,
                prefeitura_conta_id=conta_prefeitura.id,
                bairro=p["bairro"],
                cidade="Curitiba",
                uf="PR",
                ibge_municipio="4106902",
                tipo_residuo=p["tipo"],
                descricao=p["descricao"],
                lat=p["lat"],
                lng=p["lng"],
                geom=make_point_wkt(p["lat"], p["lng"]),
                status=p["status"],
            )
        )
    await db.flush()


async def seed_campanha(db: AsyncSession, *, conta_prefeitura: Conta) -> None:
    existing = await db.scalar(
        select(CampanhaPublica).where(
            CampanhaPublica.conta_organizadora_id == conta_prefeitura.id,
            CampanhaPublica.titulo.like("Mutirão%"),
        )
    )
    if existing:
        return
    db.add(
        CampanhaPublica(
            conta_organizadora_id=conta_prefeitura.id,
            titulo="Mutirão Câmbio Verde — Parque Barigui",
            descricao="Sábado das 9h às 17h. Traga recicláveis e troque por hortifrúti. Eletrônicos e pilhas também aceitos.",
            data_evento=datetime.now(tz=timezone.utc) + timedelta(days=14),
            tipo_residuo="Recicláveis + eletrônicos",
            beneficio="Hortifrúti gratuito + comprovante IPTU verde",
            cidade="Curitiba",
            uf="PR",
            ibge_municipio="4106902",
            status=CampanhaStatus.PUBLICADA,
        )
    )
    await db.flush()


async def seed_conteudo_educativo(db: AsyncSession) -> None:
    existing = await db.scalar(
        select(ConteudoEducativo).where(ConteudoEducativo.titulo == "Como prensar PET corretamente")
    )
    if existing:
        return
    db.add(
        ConteudoEducativo(
            titulo="Como prensar PET corretamente",
            resumo="3 dicas práticas para conseguir o melhor preço por kg.",
            tipo=ConteudoTipo.DICA,
            papeis_alvo=[PapelTipo.CATADOR.value, PapelTipo.COLETOR.value],
            categorias_alvo=["plasticos"],
            url=None,
            conteudo="<p>Para PET cristal valer mais: lave, seque, retire o rótulo e prense em fardos uniformes de 5kg.</p>",
            publicado=True,
        )
    )
    await db.flush()


# =============================================================================
# Runner
# =============================================================================

async def run() -> None:
    async with SessionLocal() as db:
        try:
            log.info("seed_demo_inicio")
            _, conta_cat, papel_cat = await seed_catador(db)
            usuario_cat = await db.scalar(select(Usuario).where(Usuario.email == "catador@pnr.com.br"))
            log.info("seed_demo_catador_ok")

            _, conta_comp, papel_comp, _ = await seed_comprador(db)
            usuario_comp = await db.scalar(select(Usuario).where(Usuario.email == "comprador@pnr.com.br"))
            log.info("seed_demo_comprador_ok")

            _, conta_gest, papel_gest, _ = await seed_gestor(db)
            log.info("seed_demo_gestor_ok")

            _, conta_fret, papel_fret, _ = await seed_freteiro(db)
            log.info("seed_demo_freteiro_ok")

            _, conta_pref, _ = await seed_prefeitura(db)
            log.info("seed_demo_prefeitura_ok")

            anuncios = await seed_anuncios_catador(db, conta_catador=conta_cat, papel_catador=papel_cat)
            log.info("seed_demo_anuncios_ok", count=len(anuncios))

            ofertas = await seed_ofertas_comprador(db, conta_comp=conta_comp, papel_comp=papel_comp)
            log.info("seed_demo_ofertas_ok", count=len(ofertas))

            await seed_anuncio_servico_gestor(db, conta_gestor=conta_gest, papel_gestor=papel_gest)
            await seed_anuncio_maquina(db, conta_gestor=conta_gest, papel_gestor=papel_gest)
            await seed_anuncio_frete(db, conta_freteiro=conta_fret, papel_freteiro=papel_fret)
            log.info("seed_demo_outros_anuncios_ok")

            if "pet" in anuncios and usuario_cat and usuario_comp:
                await seed_negociacao_em_andamento(
                    db,
                    anuncio_pet=anuncios["pet"],
                    conta_catador=conta_cat,
                    conta_comprador=conta_comp,
                    usuario_catador=usuario_cat,
                    usuario_comprador=usuario_comp,
                )
                log.info("seed_demo_negociacao_andamento_ok")
            if "papelao" in anuncios:
                await seed_negociacao_concluida_com_avaliacao(
                    db,
                    anuncio_papelao=anuncios["papelao"],
                    conta_catador=conta_cat,
                    conta_comprador=conta_comp,
                )
                log.info("seed_demo_negociacao_concluida_ok")

            await seed_creditos_comprador(db, conta_comp=conta_comp)
            log.info("seed_demo_creditos_ok")

            await seed_pedidos_coleta_publica(db, conta_solicitante=conta_cat, conta_prefeitura=conta_pref)
            log.info("seed_demo_pedidos_coleta_ok")

            await seed_campanha(db, conta_prefeitura=conta_pref)
            log.info("seed_demo_campanha_ok")

            await seed_conteudo_educativo(db)
            log.info("seed_demo_conteudo_ok")

            await db.commit()
            log.info("seed_demo_concluido", contas=5)
        except Exception:
            await db.rollback()
            raise


def main() -> None:
    from app.core.logging import configure_logging

    configure_logging()
    asyncio.run(run())


if __name__ == "__main__":
    main()
