import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { MobileFrame } from '@/components/MobileFrame';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { showToast } from '@/components/ui/toaster';
import { useCriarConta } from '@/hooks/useContaAtiva';
import { maskCNPJ } from '@/utils/currency';

export default function OnboardingOrgao() {
  const navigate = useNavigate();
  const criar = useCriarConta();
  const [form, setForm] = useState({
    nome_publico: '',
    cnpj: '',
    escopo: 'municipio' as 'municipio' | 'estado',
    uf: 'SP',
    ibge: '',
  });

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    criar.mutate(
      {
        tipo: 'orgao_publico',
        nome_publico: form.nome_publico,
        cnpj: form.cnpj.replace(/\D/g, ''),
        escopo_territorial: { escopo: form.escopo, uf: form.uf, ibge: form.ibge || null },
      },
      {
        onSuccess: () => {
          showToast({
            title: 'Cadastro enviado',
            description: 'Aguardando aprovação manual do administrador.',
            variant: 'info',
          });
          navigate('/perfil');
        },
        onError: (err) =>
          showToast({ title: 'Erro', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <MobileFrame>
      <TopBar title="Órgão Público" variant="dark" />
      <div className="px-screen-x py-6 space-y-4">
        <div className="rounded-lg bg-warning-light p-3 text-sm text-warning-dark">
          Contas de Órgão Público passam por <strong>aprovação manual</strong>. Acesso liberado em até 5 dias úteis.
        </div>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <Label htmlFor="nome">Nome oficial</Label>
            <Input
              id="nome"
              required
              value={form.nome_publico}
              onChange={(e) => setForm({ ...form, nome_publico: e.target.value })}
              placeholder="Ex.: Secretaria Municipal de Meio Ambiente — São Paulo"
            />
          </div>
          <div>
            <Label htmlFor="cnpj">CNPJ</Label>
            <Input
              id="cnpj"
              required
              inputMode="numeric"
              value={maskCNPJ(form.cnpj)}
              onChange={(e) => setForm({ ...form, cnpj: e.target.value })}
              className="font-mono"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>Escopo</Label>
              <Select value={form.escopo} onValueChange={(v) => setForm({ ...form, escopo: v as 'municipio' | 'estado' })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="municipio">Município</SelectItem>
                  <SelectItem value="estado">Estado</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="uf">UF</Label>
              <Input
                id="uf"
                maxLength={2}
                required
                value={form.uf}
                onChange={(e) => setForm({ ...form, uf: e.target.value.toUpperCase() })}
                className="uppercase font-mono"
              />
            </div>
          </div>
          {form.escopo === 'municipio' && (
            <div>
              <Label htmlFor="ibge">Código IBGE do município (7 dígitos)</Label>
              <Input
                id="ibge"
                inputMode="numeric"
                pattern="\d{7}"
                maxLength={7}
                value={form.ibge}
                onChange={(e) => setForm({ ...form, ibge: e.target.value.replace(/\D/g, '') })}
                className="font-mono"
              />
            </div>
          )}
          <Button type="submit" loading={criar.isPending} className="w-full">
            Enviar para aprovação
          </Button>
        </form>
      </div>
    </MobileFrame>
  );
}
