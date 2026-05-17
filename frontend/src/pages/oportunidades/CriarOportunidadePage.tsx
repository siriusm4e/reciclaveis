import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { showToast } from '@/components/ui/toaster';
import { useCategorias, useSubcategorias } from '@/hooks/useCatalogo';
import { useCriarOportunidade } from '@/hooks/useNegociacao';
import { diasUteisFromNow, toISOInputDate } from '@/utils/dates';

export default function CriarOportunidadePage() {
  const navigate = useNavigate();
  const [catId, setCatId] = useState('');
  const { data: cats } = useCategorias();
  const { data: subs } = useSubcategorias(catId || null);
  const [form, setForm] = useState({
    titulo: '',
    descricao: '',
    subcategoria_id: '',
    tipo: 'chamada_privada' as 'licitacao' | 'concorrencia' | 'chamada_publica' | 'chamada_privada',
    valor: '',
    prazo: toISOInputDate(diasUteisFromNow(5)),
    docs: '',
  });
  const criar = useCriarOportunidade();

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    criar.mutate(
      {
        titulo: form.titulo,
        descricao: form.descricao,
        subcategoria_id: form.subcategoria_id,
        tipo: form.tipo,
        documentos_exigidos: form.docs.split(',').map((s) => s.trim()).filter(Boolean),
        prazo_submissao: new Date(form.prazo).toISOString(),
        valor_estimado: form.valor ? Number(form.valor) : undefined,
      },
      {
        onSuccess: (o) => {
          showToast({ title: 'Oportunidade criada', variant: 'success' });
          navigate(`/oportunidades/${o.id}`);
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Nova oportunidade" />
      <form onSubmit={onSubmit} className="px-screen-x py-4 space-y-4 pb-32">
        <Input
          required
          minLength={5}
          placeholder="Título"
          value={form.titulo}
          onChange={(e) => setForm({ ...form, titulo: e.target.value })}
        />
        <Textarea
          required
          placeholder="Descrição detalhada"
          value={form.descricao}
          onChange={(e) => setForm({ ...form, descricao: e.target.value })}
        />
        <div className="grid grid-cols-2 gap-3">
          <Select value={catId} onValueChange={setCatId}>
            <SelectTrigger><SelectValue placeholder="Categoria" /></SelectTrigger>
            <SelectContent>{cats?.map((c) => <SelectItem key={c.id} value={c.id}>{c.nome}</SelectItem>)}</SelectContent>
          </Select>
          <Select value={form.subcategoria_id} onValueChange={(v) => setForm({ ...form, subcategoria_id: v })} disabled={!catId}>
            <SelectTrigger><SelectValue placeholder="Subcategoria" /></SelectTrigger>
            <SelectContent>{subs?.map((s) => <SelectItem key={s.id} value={s.id}>{s.nome}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <Select value={form.tipo} onValueChange={(v) => setForm({ ...form, tipo: v as 'licitacao' | 'concorrencia' | 'chamada_publica' | 'chamada_privada' })}>
          <SelectTrigger><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="chamada_privada">Chamada privada</SelectItem>
            <SelectItem value="chamada_publica">Chamada pública</SelectItem>
            <SelectItem value="licitacao">Licitação</SelectItem>
            <SelectItem value="concorrencia">Concorrência</SelectItem>
          </SelectContent>
        </Select>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label>Valor estimado (R$, opcional)</Label>
            <Input
              type="number"
              step="0.01"
              value={form.valor}
              onChange={(e) => setForm({ ...form, valor: e.target.value })}
              className="font-mono"
            />
          </div>
          <div>
            <Label>Prazo de submissão</Label>
            <Input
              type="date"
              required
              value={form.prazo}
              onChange={(e) => setForm({ ...form, prazo: e.target.value })}
            />
          </div>
        </div>
        <div>
          <Label>Documentos exigidos (slugs separados por vírgula)</Label>
          <Input
            placeholder="ex.: licenca_ambiental, cnpj_ativo"
            value={form.docs}
            onChange={(e) => setForm({ ...form, docs: e.target.value })}
            className="font-mono"
          />
        </div>
        <Button type="submit" loading={criar.isPending} className="w-full">Criar oportunidade</Button>
      </form>
    </AppLayout>
  );
}
