import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Card } from '@/components/ui/card';

export default function RegularizacaoPage() {
  return (
    <AppLayout>
      <TopBar title="Regularização" />
      <div className="px-screen-x py-4 space-y-4">
        <Card className="p-4">
          <h3 className="font-bold tracking-tight mb-2">MEI (Microempreendedor Individual)</h3>
          <p className="font-serif italic text-sm text-neutral-700 leading-relaxed">
            O MEI é a forma mais simples de formalização. Para catadores e coletores autônomos,
            o CNAE recomendado é o <span className="font-mono not-italic">3811-4/00 — Coleta de resíduos não perigosos</span>.
          </p>
          <a
            href="https://www.gov.br/empresas-e-negocios/pt-br/empreendedor"
            target="_blank"
            rel="noreferrer"
            className="text-primary-700 underline text-sm mt-2 block"
          >
            Saber mais no Portal do Empreendedor →
          </a>
        </Card>
        <Card className="p-4">
          <h3 className="font-bold tracking-tight mb-2">CNAEs comuns no setor</h3>
          <dl className="text-sm space-y-1">
            <Row codigo="3811-4/00" desc="Coleta de resíduos não perigosos" />
            <Row codigo="3812-2/00" desc="Coleta de resíduos perigosos" />
            <Row codigo="3821-1/00" desc="Tratamento e disposição de resíduos não perigosos" />
            <Row codigo="3831-9/01" desc="Recuperação de sucatas de alumínio" />
            <Row codigo="3831-9/99" desc="Recuperação de outros materiais metálicos" />
            <Row codigo="3832-7/00" desc="Recuperação de materiais plásticos" />
          </dl>
        </Card>
        <Card className="p-4 bg-info-light border-info/30">
          <h3 className="font-bold tracking-tight mb-1 text-info-dark">Importante</h3>
          <p className="text-sm text-info-dark">
            Subcategorias reguladas (hospitalar, químicos) exigem licença ambiental específica.
            A plataforma bloqueia publicação sem documento aprovado.
          </p>
        </Card>
      </div>
    </AppLayout>
  );
}

function Row({ codigo, desc }: { codigo: string; desc: string }) {
  return (
    <div className="flex gap-2">
      <dt className="font-mono text-primary-700 w-24">{codigo}</dt>
      <dd className="flex-1 text-neutral-700">{desc}</dd>
    </div>
  );
}
