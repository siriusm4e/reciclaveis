import { Truck, Wrench, Package, ShoppingCart, Briefcase, Cpu } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Card } from '@/components/ui/card';

export default function PublicarPage() {
  const navigate = useNavigate();
  return (
    <AppLayout>
      <TopBar title="Publicar" />
      <div className="px-screen-x py-4 space-y-3">
        <p className="text-sm text-neutral-700">
          O que você quer publicar?
        </p>

        <Option
          icon={<Package className="h-5 w-5" />}
          titulo="Anúncio de venda"
          descricao="Material reciclável disponível"
          tipo="venda"
          onClick={() => navigate('/anuncios/criar')}
        />
        <Option
          icon={<ShoppingCart className="h-5 w-5" />}
          titulo="Oferta de compra"
          descricao="Demanda de material"
          tipo="compra"
          onClick={() => navigate('/ofertas/criar')}
        />
        <Option
          icon={<Cpu className="h-5 w-5" />}
          titulo="Equipamento"
          descricao="Máquina à venda ou aluguel"
          tipo="neutro"
          onClick={() => navigate('/maquinas/criar')}
        />
        <Option
          icon={<Wrench className="h-5 w-5" />}
          titulo="Serviço"
          descricao="Manutenção, gestão, consultoria"
          tipo="neutro"
          onClick={() => navigate('/servicos/criar')}
        />
        <Option
          icon={<Truck className="h-5 w-5" />}
          titulo="Frete"
          descricao="Disponibilidade de transporte"
          tipo="neutro"
          onClick={() => navigate('/fretes/criar')}
        />
        <Option
          icon={<Briefcase className="h-5 w-5" />}
          titulo="Oportunidade / Licitação"
          descricao="Chamada pública ou privada"
          tipo="neutro"
          onClick={() => navigate('/oportunidades/criar')}
        />
      </div>
    </AppLayout>
  );
}

function Option({
  icon,
  titulo,
  descricao,
  tipo,
  onClick,
}: {
  icon: React.ReactNode;
  titulo: string;
  descricao: string;
  tipo: 'venda' | 'compra' | 'neutro';
  onClick: () => void;
}) {
  const accent =
    tipo === 'venda'
      ? 'border-l-primary-500'
      : tipo === 'compra'
      ? 'border-l-accent-500'
      : 'border-l-neutral-300';
  return (
    <button type="button" onClick={onClick} className="w-full text-left">
      <Card className={`flex items-center gap-3 p-3 border-l-4 ${accent} transition-colors hover:bg-neutral-50`}>
        <div className="rounded-full bg-neutral-100 p-2 text-neutral-700">{icon}</div>
        <div className="flex-1">
          <h3 className="text-sm font-bold tracking-tight text-neutral-900">{titulo}</h3>
          <p className="text-xs text-neutral-600">{descricao}</p>
        </div>
      </Card>
    </button>
  );
}
