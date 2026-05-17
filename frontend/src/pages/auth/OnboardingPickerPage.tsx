import { Building2, Landmark, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { MobileFrame } from '@/components/MobileFrame';
import { TopBar } from '@/components/TopBar';
import { Card } from '@/components/ui/card';

export default function OnboardingPickerPage() {
  const navigate = useNavigate();
  return (
    <MobileFrame>
      <TopBar title="Tipo de conta" back={false} />
      <div className="px-screen-x py-6">
        <h2 className="mb-4 text-lg text-neutral-700">
          Como você vai usar a plataforma?
        </h2>
        <div className="space-y-3">
          <Option
            icon={<User className="h-6 w-6" />}
            titulo="Pessoa Física"
            descricao="Catador, coletor autônomo, gerador eventual"
            onClick={() => navigate('/onboarding/pf')}
          />
          <Option
            icon={<Building2 className="h-6 w-6" />}
            titulo="Pessoa Jurídica"
            descricao="Comprador, gestor de resíduos, freteiro, indústria"
            onClick={() => navigate('/onboarding/pj')}
          />
          <Option
            icon={<Landmark className="h-6 w-6" />}
            titulo="Órgão Público"
            descricao="Prefeitura, órgão estadual (requer aprovação)"
            onClick={() => navigate('/onboarding/orgao')}
          />
        </div>
        <p className="mt-6 text-xs text-neutral-500">
          O tipo é <strong>imutável</strong> após criação. Para mudar, crie uma nova Conta.
        </p>
      </div>
    </MobileFrame>
  );
}

function Option({
  icon,
  titulo,
  descricao,
  onClick,
}: {
  icon: React.ReactNode;
  titulo: string;
  descricao: string;
  onClick: () => void;
}) {
  return (
    <button type="button" onClick={onClick} className="w-full text-left">
      <Card className="flex items-start gap-3 p-4 transition-colors hover:border-primary-500 hover:bg-primary-50">
        <div className="rounded-full bg-primary-100 p-2.5 text-primary-700">{icon}</div>
        <div className="flex-1">
          <h3 className="text-base font-bold tracking-tight text-neutral-900">{titulo}</h3>
          <p className="text-sm text-neutral-600">{descricao}</p>
        </div>
      </Card>
    </button>
  );
}
