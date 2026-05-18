import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { CenterSpinner } from '@/components/ui/states';
import { showToast } from '@/components/ui/toaster';
import { useContaAtiva, useEstabelecimentos, usePapeis } from '@/hooks/useContaAtiva';
import { useTiposDocumento, useUploadDocumento } from '@/hooks/useDocumentos';
import type { TipoDocumento } from '@/types/api';

export default function UploadDocPage() {
  const navigate = useNavigate();
  const conta = useContaAtiva();
  const upload = useUploadDocumento();

  // Filtro opcional por papel ativo — mostra só os tipos aplicáveis
  const { data: papeis } = usePapeis(conta?.id ?? null);
  const papeisAtivos = papeis?.filter((p) => p.status === 'ativo') ?? [];
  const [papelSlug, setPapelSlug] = useState<string>('');

  const { data: tipos, isLoading: loadingTipos } = useTiposDocumento(papelSlug || undefined);
  const { data: estabs } = useEstabelecimentos(conta?.id ?? null);

  const [tipoId, setTipoId] = useState<string>('');
  const [estabId, setEstabId] = useState<string>('');
  const [numero, setNumero] = useState('');
  const [emissao, setEmissao] = useState('');
  const [venc, setVenc] = useState('');
  const [file, setFile] = useState<File | null>(null);

  const tipoSelecionado: TipoDocumento | undefined = useMemo(
    () => tipos?.find((t) => t.id === tipoId),
    [tipos, tipoId],
  );

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      showToast({ title: 'Selecione um arquivo', variant: 'warning' });
      return;
    }
    if (!tipoId) {
      showToast({ title: 'Selecione o tipo de documento', variant: 'warning' });
      return;
    }
    if (tipoSelecionado?.tem_vencimento && !venc) {
      showToast({ title: 'Este tipo exige data de vencimento', variant: 'warning' });
      return;
    }
    if (tipoSelecionado?.escopo === 'estabelecimento' && !estabId) {
      showToast({ title: 'Este tipo é por Estabelecimento — selecione um', variant: 'warning' });
      return;
    }
    upload.mutate(
      {
        file,
        tipo_documento_id: tipoId,
        estabelecimento_id: tipoSelecionado?.escopo === 'estabelecimento' ? estabId : undefined,
        numero: numero || undefined,
        data_emissao: emissao || undefined,
        data_vencimento: venc || undefined,
      },
      {
        onSuccess: (doc) => {
          showToast({
            title: 'Documento enviado',
            description:
              doc.status === 'aprovado'
                ? 'Aprovado automaticamente.'
                : 'Aguardando análise da equipe.',
            variant: 'success',
          });
          navigate('/documentos');
        },
        onError: (err) =>
          showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Enviar documento" />
      <form onSubmit={onSubmit} className="px-screen-x py-4 space-y-4 pb-12">
        {/* Filtro opcional por papel — só aparece se conta tem 2+ papeis ativos */}
        {papeisAtivos.length > 1 && (
          <div>
            <Label>Filtrar por papel (opcional)</Label>
            <Select
              value={papelSlug || '__todos'}
              onValueChange={(v) => {
                setPapelSlug(v === '__todos' ? '' : v);
                setTipoId('');
              }}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="__todos">Todos os papéis</SelectItem>
                {papeisAtivos.map((p) => (
                  <SelectItem key={p.id} value={p.papel}>
                    {p.papel.replace('_', ' ')}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        <div>
          <Label htmlFor="tipo">Tipo de documento</Label>
          {loadingTipos ? (
            <CenterSpinner label="Carregando tipos..." />
          ) : (
            <Select
              value={tipoId}
              onValueChange={(v) => {
                setTipoId(v);
                setEstabId('');
              }}
            >
              <SelectTrigger id="tipo">
                <SelectValue
                  placeholder={tipos?.length ? 'Selecione o tipo' : 'Nenhum tipo cadastrado'}
                />
              </SelectTrigger>
              <SelectContent>
                {tipos?.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.nome}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          {tipoSelecionado && (
            <Card className="mt-2 p-3 bg-info-light border-info/30">
              <div className="text-xs text-info-dark space-y-1">
                {tipoSelecionado.descricao && <p>{tipoSelecionado.descricao}</p>}
                <p>
                  Escopo: <strong>{tipoSelecionado.escopo === 'conta' ? 'Conta' : 'Estabelecimento'}</strong>
                  {tipoSelecionado.tem_vencimento && ' · Tem vencimento'}
                  {tipoSelecionado.exige_aprovacao_manual
                    ? ' · Aprovação manual'
                    : ' · Aprovação automática'}
                  {tipoSelecionado.obrigatorio && ' · Obrigatório'}
                </p>
                {tipoSelecionado.papeis_aplicaveis.length > 0 && (
                  <p className="font-mono text-[10px]">
                    Aplica a: {tipoSelecionado.papeis_aplicaveis.join(', ')}
                  </p>
                )}
              </div>
            </Card>
          )}
        </div>

        {tipoSelecionado?.escopo === 'estabelecimento' && (
          <div>
            <Label>Estabelecimento</Label>
            <Select value={estabId} onValueChange={setEstabId}>
              <SelectTrigger>
                <SelectValue
                  placeholder={estabs?.length ? 'Selecione' : 'Cadastre um estabelecimento primeiro'}
                />
              </SelectTrigger>
              <SelectContent>
                {estabs?.map((e) => (
                  <SelectItem key={e.id} value={e.id}>
                    {e.nome} — {e.cidade}/{e.uf}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        <div>
          <Label htmlFor="file">Arquivo (PDF, JPG, PNG, WebP — máx. 10MB)</Label>
          <Input
            id="file"
            type="file"
            accept="application/pdf,image/jpeg,image/png,image/webp"
            required
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label>Número (opcional)</Label>
            <Input value={numero} onChange={(e) => setNumero(e.target.value)} className="font-mono" />
          </div>
          <div>
            <Label>Emissão (opcional)</Label>
            <Input type="date" value={emissao} onChange={(e) => setEmissao(e.target.value)} />
          </div>
        </div>

        {tipoSelecionado?.tem_vencimento && (
          <div>
            <Label>Vencimento *</Label>
            <Input type="date" required value={venc} onChange={(e) => setVenc(e.target.value)} />
            <p className="text-xs text-neutral-500 mt-1">
              Avisos automáticos em D-30, D-15 e D-7. Após o vencimento, o status muda para
              <span className="font-mono"> vencido</span>.
            </p>
          </div>
        )}

        <Button
          type="submit"
          loading={upload.isPending}
          className="w-full"
          disabled={!tipos?.length}
        >
          Enviar para análise
        </Button>
      </form>
    </AppLayout>
  );
}
