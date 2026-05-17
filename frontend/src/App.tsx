import { useEffect } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';

import { RequireAuth } from '@/components/RequireAuth';
import { Toaster } from '@/components/ui/toaster';
import { useAutoSelecionarConta } from '@/hooks/useContaAtiva';
import { useNotificacoesRealtime } from '@/hooks/useNotificacoes';
import { usePushNotifications } from '@/hooks/usePushNotifications';

import LoginPage from '@/pages/auth/LoginPage';
import RegisterPage from '@/pages/auth/RegisterPage';
import MfaSetupPage from '@/pages/auth/MfaSetupPage';
import OnboardingPickerPage from '@/pages/auth/OnboardingPickerPage';
import OnboardingPF from '@/pages/auth/OnboardingPF';
import OnboardingPJ from '@/pages/auth/OnboardingPJ';
import OnboardingOrgao from '@/pages/auth/OnboardingOrgao';
import ConvitePage from '@/pages/auth/ConvitePage';

import HomePage from '@/pages/home/HomePage';
import NotificacoesPage from '@/pages/home/NotificacoesPage';

import MarketplaceBuscarPage from '@/pages/marketplace/BuscarPage';
import MarketplacePublicarPage from '@/pages/marketplace/PublicarPage';
import AnuncioDetalhePage from '@/pages/marketplace/AnuncioDetalhePage';
import OfertaDetalhePage from '@/pages/marketplace/OfertaDetalhePage';
import CriarAnuncioPage from '@/pages/marketplace/CriarAnuncioPage';
import CriarOfertaPage from '@/pages/marketplace/CriarOfertaPage';
import AlertaPagoPage from '@/pages/marketplace/AlertaPagoPage';

import MaquinasListPage from '@/pages/maquinas/MaquinasListPage';
import MaquinaDetalhePage from '@/pages/maquinas/MaquinaDetalhePage';
import CriarMaquinaPage from '@/pages/maquinas/CriarMaquinaPage';

import ServicosListPage from '@/pages/servicos/ServicosListPage';
import ServicoDetalhePage from '@/pages/servicos/ServicoDetalhePage';
import CriarServicoPage from '@/pages/servicos/CriarServicoPage';

import FretesListPage from '@/pages/servicos/FretesListPage';
import CriarFretePage from '@/pages/servicos/CriarFretePage';

import OportunidadesListPage from '@/pages/oportunidades/OportunidadesListPage';
import OportunidadeDetalhePage from '@/pages/oportunidades/OportunidadeDetalhePage';
import CriarOportunidadePage from '@/pages/oportunidades/CriarOportunidadePage';

import NegociacoesListPage from '@/pages/negociacoes/NegociacoesListPage';
import NegociacaoChatPage from '@/pages/negociacoes/NegociacaoChatPage';
import AvaliarPage from '@/pages/negociacoes/AvaliarPage';

import PerfilPage from '@/pages/perfil/PerfilPage';
import ReputacaoPage from '@/pages/perfil/ReputacaoPage';
import MembrosPage from '@/pages/perfil/MembrosPage';
import PapelConfigPage from '@/pages/perfil/PapelConfigPage';
import TrocarContaPage from '@/pages/perfil/TrocarContaPage';

import DocumentosPage from '@/pages/documentos/DocumentosPage';
import UploadDocPage from '@/pages/documentos/UploadDocPage';
import RegularizacaoPage from '@/pages/documentos/RegularizacaoPage';

import CreditosPage from '@/pages/creditos/CreditosPage';
import ComprarPacotePage from '@/pages/creditos/ComprarPacotePage';
import HistoricoTransacoesPage from '@/pages/creditos/HistoricoTransacoesPage';

import PlanoAtualPage from '@/pages/assinaturas/PlanoAtualPage';
import UpgradePlanoPage from '@/pages/assinaturas/UpgradePlanoPage';
import FaturasPage from '@/pages/assinaturas/FaturasPage';

import PedidoColetaPage from '@/pages/institucional/PedidoColetaPage';
import CampanhasPage from '@/pages/institucional/CampanhasPage';
import MapaInstitucionalPage from '@/pages/institucional/MapaInstitucionalPage';

import ConteudoListPage from '@/pages/conteudo/ConteudoListPage';
import ConteudoDetalhePage from '@/pages/conteudo/ConteudoDetalhePage';
import PreferenciasPage from '@/pages/conteudo/PreferenciasPage';

import AdminShell from '@/pages/admin/AdminShell';
import AdminDashboard from '@/pages/admin/AdminDashboard';
import AdminContas from '@/pages/admin/ContasAdmin';
import AdminDocumentos from '@/pages/admin/DocumentosAdmin';
import AdminCatalogo from '@/pages/admin/CatalogoAdmin';
import AdminCreditos from '@/pages/admin/CreditosAdmin';
import AdminAssinaturas from '@/pages/admin/AssinaturasAdmin';
import AdminModeracao from '@/pages/admin/ModeracaoAdmin';
import AdminConteudo from '@/pages/admin/ConteudoAdmin';
import AdminAnalytics from '@/pages/admin/AnalyticsAdmin';
import AdminPerfis from '@/pages/admin/PerfisAdmin';
import AdminAuditLog from '@/pages/admin/AuditLogAdmin';

export function App() {
  // Inicializa side-effects globais quando autenticado
  useAutoSelecionarConta();
  useNotificacoesRealtime();
  usePushNotifications();

  // Foco no topo a cada mudança de rota (UX mobile)
  useEffect(() => {
    const handler = () => window.scrollTo(0, 0);
    window.addEventListener('popstate', handler);
    return () => window.removeEventListener('popstate', handler);
  }, []);

  return (
    <>
      <Routes>
        <Route path="/" element={<Navigate to="/home" replace />} />

        {/* Auth */}
        <Route path="/auth/login" element={<LoginPage />} />
        <Route path="/auth/cadastro" element={<RegisterPage />} />
        <Route path="/auth/mfa/setup" element={<RequireAuth><MfaSetupPage /></RequireAuth>} />
        <Route path="/auth/convite/:token" element={<ConvitePage />} />

        {/* Onboarding */}
        <Route path="/onboarding" element={<RequireAuth><OnboardingPickerPage /></RequireAuth>} />
        <Route path="/onboarding/pf" element={<RequireAuth><OnboardingPF /></RequireAuth>} />
        <Route path="/onboarding/pj" element={<RequireAuth><OnboardingPJ /></RequireAuth>} />
        <Route path="/onboarding/orgao" element={<RequireAuth><OnboardingOrgao /></RequireAuth>} />

        {/* Home + notificações */}
        <Route path="/home" element={<RequireAuth><HomePage /></RequireAuth>} />
        <Route path="/notificacoes" element={<RequireAuth><NotificacoesPage /></RequireAuth>} />

        {/* Marketplace */}
        <Route path="/marketplace/buscar" element={<RequireAuth><MarketplaceBuscarPage /></RequireAuth>} />
        <Route path="/marketplace/publicar" element={<RequireAuth><MarketplacePublicarPage /></RequireAuth>} />
        <Route path="/anuncios/:id" element={<RequireAuth><AnuncioDetalhePage /></RequireAuth>} />
        <Route path="/anuncios/criar" element={<RequireAuth><CriarAnuncioPage /></RequireAuth>} />
        <Route path="/ofertas/:id" element={<RequireAuth><OfertaDetalhePage /></RequireAuth>} />
        <Route path="/ofertas/criar" element={<RequireAuth><CriarOfertaPage /></RequireAuth>} />
        <Route path="/ofertas/:id/alerta-pago" element={<RequireAuth><AlertaPagoPage /></RequireAuth>} />

        {/* Máquinas / Serviços / Fretes */}
        <Route path="/maquinas" element={<RequireAuth><MaquinasListPage /></RequireAuth>} />
        <Route path="/maquinas/:id" element={<RequireAuth><MaquinaDetalhePage /></RequireAuth>} />
        <Route path="/maquinas/criar" element={<RequireAuth><CriarMaquinaPage /></RequireAuth>} />
        <Route path="/servicos" element={<RequireAuth><ServicosListPage /></RequireAuth>} />
        <Route path="/servicos/:id" element={<RequireAuth><ServicoDetalhePage /></RequireAuth>} />
        <Route path="/servicos/criar" element={<RequireAuth><CriarServicoPage /></RequireAuth>} />
        <Route path="/fretes" element={<RequireAuth><FretesListPage /></RequireAuth>} />
        <Route path="/fretes/criar" element={<RequireAuth><CriarFretePage /></RequireAuth>} />

        {/* Oportunidades */}
        <Route path="/oportunidades" element={<RequireAuth><OportunidadesListPage /></RequireAuth>} />
        <Route path="/oportunidades/:id" element={<RequireAuth><OportunidadeDetalhePage /></RequireAuth>} />
        <Route path="/oportunidades/criar" element={<RequireAuth><CriarOportunidadePage /></RequireAuth>} />

        {/* Negociações */}
        <Route path="/negociacoes" element={<RequireAuth><NegociacoesListPage /></RequireAuth>} />
        <Route path="/negociacoes/:id" element={<RequireAuth><NegociacaoChatPage /></RequireAuth>} />
        <Route path="/negociacoes/:id/avaliar" element={<RequireAuth><AvaliarPage /></RequireAuth>} />

        {/* Perfil / membros / papéis */}
        <Route path="/perfil" element={<RequireAuth><PerfilPage /></RequireAuth>} />
        <Route path="/perfil/reputacao" element={<RequireAuth><ReputacaoPage /></RequireAuth>} />
        <Route path="/perfil/membros" element={<RequireAuth><MembrosPage /></RequireAuth>} />
        <Route path="/perfil/papeis/:id" element={<RequireAuth><PapelConfigPage /></RequireAuth>} />
        <Route path="/perfil/trocar-conta" element={<RequireAuth><TrocarContaPage /></RequireAuth>} />

        {/* Documentos */}
        <Route path="/documentos" element={<RequireAuth><DocumentosPage /></RequireAuth>} />
        <Route path="/documentos/upload" element={<RequireAuth><UploadDocPage /></RequireAuth>} />
        <Route path="/documentos/regularizacao" element={<RequireAuth><RegularizacaoPage /></RequireAuth>} />

        {/* Créditos / assinaturas */}
        <Route path="/creditos" element={<RequireAuth><CreditosPage /></RequireAuth>} />
        <Route path="/creditos/comprar" element={<RequireAuth><ComprarPacotePage /></RequireAuth>} />
        <Route path="/creditos/historico" element={<RequireAuth><HistoricoTransacoesPage /></RequireAuth>} />
        <Route path="/assinaturas" element={<RequireAuth><PlanoAtualPage /></RequireAuth>} />
        <Route path="/assinaturas/upgrade" element={<RequireAuth><UpgradePlanoPage /></RequireAuth>} />
        <Route path="/faturas" element={<RequireAuth><FaturasPage /></RequireAuth>} />

        {/* Institucional */}
        <Route path="/coleta-publica" element={<RequireAuth><PedidoColetaPage /></RequireAuth>} />
        <Route path="/campanhas" element={<RequireAuth><CampanhasPage /></RequireAuth>} />
        <Route path="/mapa-institucional" element={<RequireAuth><MapaInstitucionalPage /></RequireAuth>} />

        {/* Conteúdo */}
        <Route path="/conteudo" element={<RequireAuth><ConteudoListPage /></RequireAuth>} />
        <Route path="/conteudo/:id" element={<RequireAuth><ConteudoDetalhePage /></RequireAuth>} />
        <Route path="/configuracoes/preferencias" element={<RequireAuth><PreferenciasPage /></RequireAuth>} />

        {/* Admin (Web only) */}
        <Route path="/admin" element={<RequireAuth><AdminShell /></RequireAuth>}>
          <Route index element={<AdminDashboard />} />
          <Route path="contas" element={<AdminContas />} />
          <Route path="documentos" element={<AdminDocumentos />} />
          <Route path="catalogo" element={<AdminCatalogo />} />
          <Route path="creditos" element={<AdminCreditos />} />
          <Route path="assinaturas" element={<AdminAssinaturas />} />
          <Route path="moderacao" element={<AdminModeracao />} />
          <Route path="conteudo" element={<AdminConteudo />} />
          <Route path="analytics" element={<AdminAnalytics />} />
          <Route path="perfis" element={<AdminPerfis />} />
          <Route path="audit-log" element={<AdminAuditLog />} />
        </Route>

        <Route path="*" element={<Navigate to="/home" replace />} />
      </Routes>
      <Toaster />
    </>
  );
}
