import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { ConditionSelector } from '@/components/ConditionSelector';
import { MapPicker } from '@/components/MapPicker';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { showToast } from '@/components/ui/toaster';
import { useCriarAnuncio } from '@/hooks/useAnuncios';
import { useCategorias, useSubcategorias, useTiposMaterial } from '@/hooks/useCatalogo';
import { useContaAtiva, usePapeis } from '@/hooks/useContaAtiva';
import { useGeolocalizacao } from '@/hooks/useGeolocalizacao';
import type { CondicaoForma, CondicaoLimpeza, CondicaoUmidade } from '@/types/api';
import { SAO_PAULO_CAPITAL, type LatLng } from '@/utils/geo';
import { toISOInputDate } from '@/utils/dates';

const MAX_FOTOS = 3;

export default function CriarAnuncioPage() {
  const navigate = useNavigate();
  const conta = useContaAtiva();
  const { obterPosicao } = useGeolocalizacao();
  const { data: categorias } = useCategorias();
  const { data: papeis } = usePapeis(conta?.id ?? null);

  // === Cascata: Categoria → Subcategoria → TipoMaterial ===
  const [categoriaId, setCategoriaId] = useState<string>('');
  const [subcategoriaId, setSubcategoriaId] = useState<string>('');
  const [tipoMaterialId, setTipoMaterialId] = useState<string>('');
  const { data: subcategorias } = useSubcategorias(categoriaId || null);
  const { data: tipos } = useTiposMaterial(subcategoriaId || null);

  // Reset dropdowns dependentes quando o nível superior muda
  useEffect(() => {
    setSubcategoriaId('');
    setTipoMaterialId('');
  }, [categoriaId]);
  useEffect(() => {
    setTipoMaterialId('');
  }, [subcategoriaId]);

  const subSelecionada = subcategorias?.find((s) => s.id === subcategoriaId);
  const tipoSelecionado = tipos?.find((t) => t.id === tipoMaterialId);

  const [form, setForm] = useState({
    papel_id: '',
    preco_pretendido: '',
    unidade: 'kg',
    volume_estimado: '',
    territorio: 'urbano' as 'urbano' | 'rural',
    frequencia: 'lote_unico' as 'lote_unico' | 'recorrente',
    intervalo_geracao: '',
    prazo_validade: toISOInputDate(new Date(Date.now() + 30 * 86400_000)),
    raio_km: 25,
  });
  const [condicaoLimpeza, setCondicaoLimpeza] = useState<CondicaoLimpeza | null>(null);
  const [condicaoUmidade, setCondicaoUmidade] = useState<CondicaoUmidade | null>(null);
  const [condicaoForma, setCondicaoForma] = useState<CondicaoForma | null>(null);
  const [fotos, setFotos] = useState<string[]>([]);
  const [loc, setLoc] = useState<LatLng>(SAO_PAULO_CAPITAL);

  useEffect(() => {
    void obterPosicao().then((p) => setLoc(p));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Quando o tipo é escolhido, herda a unidade padrão dele
  useEffect(() => {
    if (tipoSelecionado) setForm((f) => ({ ...f, unidade: tipoSelecionado.unidade_padrao }));
  }, [tipoSelecionado]);

  const criar = useCriarAnuncio();

  // Restante do formulário só libera após Tipo selecionado (3º dropdown)
  const tipoEscolhido = Boolean(tipoMaterialId);

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.papel_id || !tipoMaterialId) {
      showToast({ title: 'Selecione Papel, Categoria, Subcategoria e Tipo', variant: 'warning' });
      return;
    }
    if (fotos.length > MAX_FOTOS) {
      showToast({ title: `Máximo de ${MAX_FOTOS} fotos`, variant: 'warning' });
      return;
    }
    criar.mutate(
      {
        papel_id: form.papel_id,
        tipo_material_id: tipoMaterialId,
        atributos: {},
        condicao_limpeza: condicaoLimpeza ?? undefined,
        condicao_umidade: condicaoUmidade ?? undefined,
        condicao_forma: condicaoForma ?? undefined,
        localizacao_real: loc,
        territorio: form.territorio,
        preco_pretendido: Number(form.preco_pretendido),
        unidade: form.unidade,
        volume_estimado: form.volume_estimado ? Number(form.volume_estimado) : undefined,
        frequencia: form.frequencia,
        intervalo_geracao: form.frequencia === 'recorrente' ? form.intervalo_geracao : undefined,
        prazo_validade: new Date(form.prazo_validade).toISOString(),
        fotos,
      },
      {
        onSuccess: (a) => {
          showToast({ title: 'Anúncio publicado', variant: 'success' });
          navigate(`/anuncios/${a.id}`);
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  const papelAtivos = papeis?.filter((p) => p.status === 'ativo') ?? [];

  return (
    <AppLayout>
      <TopBar title="Novo anúncio de venda" />
      <form onSubmit={onSubmit} className="px-screen-x py-4 space-y-4 pb-32">
        <div>
          <Label>Papel que está publicando</Label>
          <Select value={form.papel_id} onValueChange={(v) => setForm({ ...form, papel_id: v })}>
            <SelectTrigger><SelectValue placeholder="Escolha um papel ativo" /></SelectTrigger>
            <SelectContent>
              {papelAtivos.length === 0 ? (
                <SelectItem value="_" disabled>Sem papéis ativos — ative em Perfil</SelectItem>
              ) : (
                papelAtivos.map((p) => (
                  <SelectItem key={p.id} value={p.id}>{p.papel.replace('_', ' ')}</SelectItem>
                ))
              )}
            </SelectContent>
          </Select>
        </div>

        {/* === 3 dropdowns encadeados === */}
        <div className="space-y-3">
          <div>
            <Label>Categoria</Label>
            <Select value={categoriaId} onValueChange={setCategoriaId}>
              <SelectTrigger><SelectValue placeholder="Selecione" /></SelectTrigger>
              <SelectContent>
                {categorias?.map((c) => (
                  <SelectItem key={c.id} value={c.id}>{c.nome}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Subcategoria</Label>
            <Select
              value={subcategoriaId}
              onValueChange={setSubcategoriaId}
              disabled={!categoriaId}
            >
              <SelectTrigger>
                <SelectValue placeholder={categoriaId ? 'Selecione' : 'Escolha uma categoria primeiro'} />
              </SelectTrigger>
              <SelectContent>
                {subcategorias?.map((s) => (
                  <SelectItem key={s.id} value={s.id}>{s.nome}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Tipo de Material</Label>
            <Select
              value={tipoMaterialId}
              onValueChange={setTipoMaterialId}
              disabled={!subcategoriaId}
            >
              <SelectTrigger>
                <SelectValue placeholder={subcategoriaId ? 'Selecione' : 'Escolha uma subcategoria primeiro'} />
              </SelectTrigger>
              <SelectContent>
                {tipos?.map((t) => (
                  <SelectItem key={t.id} value={t.id}>{t.nome}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {subSelecionada?.requer_validacao_documental && (
          <div className="rounded-lg bg-warning-light p-2 text-xs text-warning-dark">
            Subcategoria regulada — exige documentos aprovados:{' '}
            <span className="font-mono">{subSelecionada.documentos_exigidos.join(', ')}</span>
          </div>
        )}

        {/* O restante só fica disponível após escolher o Tipo (3º dropdown) */}
        <div className={tipoEscolhido ? '' : 'pointer-events-none opacity-40'} aria-disabled={!tipoEscolhido}>
          {/* === Condição (3 grupos exclusivos) === */}
          <div className="space-y-3 rounded-lg border border-neutral-200 p-3">
            <p className="text-sm font-semibold text-neutral-800">Condição do material</p>
            <ConditionSelector group="limpeza" value={condicaoLimpeza} onChange={setCondicaoLimpeza} />
            <ConditionSelector group="umidade" value={condicaoUmidade} onChange={setCondicaoUmidade} />
            <ConditionSelector group="forma" value={condicaoForma} onChange={setCondicaoForma} />
          </div>

          <div className="grid grid-cols-2 gap-3 mt-4">
            <div>
              <Label htmlFor="preco">Preço (R$)</Label>
              <Input
                id="preco"
                type="number"
                step="0.01"
                min="0"
                required={tipoEscolhido}
                value={form.preco_pretendido}
                onChange={(e) => setForm({ ...form, preco_pretendido: e.target.value })}
                className="font-mono"
              />
            </div>
            <div>
              <Label htmlFor="unidade">Unidade</Label>
              <Input
                id="unidade"
                value={form.unidade}
                onChange={(e) => setForm({ ...form, unidade: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="volume">Volume estimado</Label>
              <Input
                id="volume"
                type="number"
                step="0.01"
                value={form.volume_estimado}
                onChange={(e) => setForm({ ...form, volume_estimado: e.target.value })}
                className="font-mono"
                placeholder="ex.: 50"
              />
            </div>
            <div>
              <Label>Frequência</Label>
              <Select value={form.frequencia} onValueChange={(v) => setForm({ ...form, frequencia: v as 'lote_unico' | 'recorrente' })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="lote_unico">Lote único</SelectItem>
                  <SelectItem value="recorrente">Recorrente</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {form.frequencia === 'recorrente' && (
            <div className="mt-4">
              <Label htmlFor="intervalo">Intervalo</Label>
              <Input
                id="intervalo"
                required={form.frequencia === 'recorrente'}
                placeholder="ex.: semanal, mensal"
                value={form.intervalo_geracao}
                onChange={(e) => setForm({ ...form, intervalo_geracao: e.target.value })}
              />
            </div>
          )}

          {/* === Raio de divulgação (slider 1-500km) === */}
          <div className="mt-4">
            <div className="flex items-baseline justify-between">
              <Label>Raio de divulgação</Label>
              <span className="font-mono text-sm font-semibold text-primary-700">{form.raio_km} km</span>
            </div>
            <input
              type="range"
              min={1}
              max={500}
              step={1}
              value={form.raio_km}
              onChange={(e) => setForm({ ...form, raio_km: Number(e.target.value) })}
              className="w-full accent-primary-500"
              aria-label="Raio em km, mínimo 1, máximo 500"
            />
            <div className="flex justify-between text-[10px] text-neutral-500">
              <span>1 km</span>
              <span>500 km</span>
            </div>
          </div>

          {/* === Território === */}
          <div className="mt-4">
            <Label>Território</Label>
            <Select value={form.territorio} onValueChange={(v) => setForm({ ...form, territorio: v as 'urbano' | 'rural' })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="urbano">Urbano</SelectItem>
                <SelectItem value="rural">Rural</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* === Validade === */}
          <div className="mt-4">
            <Label htmlFor="prazo">Válido até</Label>
            <Input
              id="prazo"
              type="date"
              required={tipoEscolhido}
              value={form.prazo_validade}
              onChange={(e) => setForm({ ...form, prazo_validade: e.target.value })}
            />
          </div>

          {/* === Fotos: opcionais, máximo 3 === */}
          <div className="mt-4">
            <div className="flex items-baseline justify-between">
              <Label>Fotos (opcional)</Label>
              <span className="text-xs text-neutral-500 font-mono">{fotos.length}/{MAX_FOTOS}</span>
            </div>
            <div className="flex flex-wrap gap-2 mt-1">
              {fotos.map((f, i) => (
                <div key={i} className="relative">
                  <img src={f} alt={`Foto ${i + 1}`} className="h-16 w-16 rounded-md object-cover" />
                  <button
                    type="button"
                    onClick={() => setFotos(fotos.filter((_, idx) => idx !== i))}
                    className="absolute -top-1 -right-1 rounded-full bg-neutral-900 text-white h-5 w-5 text-xs"
                    aria-label="Remover foto"
                  >
                    ×
                  </button>
                </div>
              ))}
              {fotos.length < MAX_FOTOS && (
                <label className="flex h-16 w-16 cursor-pointer items-center justify-center rounded-md border-2 border-dashed border-neutral-300 text-2xl text-neutral-400 hover:border-primary-300">
                  +
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      // Upload real seria via presigned URL — aqui usamos object URL como placeholder
                      const url = URL.createObjectURL(file);
                      setFotos((prev) => (prev.length < MAX_FOTOS ? [...prev, url] : prev));
                      e.target.value = '';
                    }}
                  />
                </label>
              )}
            </div>
          </div>

          <div className="mt-4">
            <Label>Localização (arraste o pin)</Label>
            <MapPicker value={loc} onChange={setLoc} height={240} />
            <p className="mt-1 text-[10px] text-neutral-500">
              Será publicada com offset de privacidade ({form.territorio === 'urbano' ? '~250m' : '~1.5km'}).
            </p>
          </div>
        </div>

        <Button
          type="submit"
          loading={criar.isPending}
          disabled={!tipoEscolhido}
          className="w-full"
        >
          {tipoEscolhido ? 'Publicar anúncio' : 'Selecione Tipo de Material para continuar'}
        </Button>
      </form>
    </AppLayout>
  );
}
