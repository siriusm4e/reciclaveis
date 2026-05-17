import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { extractErrorMessage } from '@/api/client';
import { AppLayout } from '@/components/AppLayout';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { showToast } from '@/components/ui/toaster';
import { useUploadDocumento } from '@/hooks/useDocumentos';

export default function UploadDocPage() {
  const navigate = useNavigate();
  const upload = useUploadDocumento();
  const [tipoId, setTipoId] = useState('');
  const [numero, setNumero] = useState('');
  const [emissao, setEmissao] = useState('');
  const [venc, setVenc] = useState('');
  const [file, setFile] = useState<File | null>(null);

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      showToast({ title: 'Selecione um arquivo', variant: 'warning' });
      return;
    }
    upload.mutate(
      {
        file,
        tipo_documento_id: tipoId,
        numero: numero || undefined,
        data_emissao: emissao || undefined,
        data_vencimento: venc || undefined,
      },
      {
        onSuccess: () => {
          showToast({ title: 'Documento enviado', description: 'Aguardando análise.', variant: 'success' });
          navigate('/documentos');
        },
        onError: (err) => showToast({ title: 'Falha', description: extractErrorMessage(err), variant: 'error' }),
      },
    );
  };

  return (
    <AppLayout>
      <TopBar title="Enviar documento" />
      <form onSubmit={onSubmit} className="px-screen-x py-4 space-y-4">
        <div>
          <Label>ID do Tipo de Documento</Label>
          <Input
            required
            value={tipoId}
            onChange={(e) => setTipoId(e.target.value)}
            placeholder="UUID do tipo (admin do catálogo)"
            className="font-mono text-xs"
          />
          <p className="text-xs text-neutral-500 mt-1">
            Em produção: dropdown filtrado por papel ativo. No MVP, cole o UUID do tipo desejado.
          </p>
        </div>
        <div>
          <Label>Arquivo (PDF, JPG, PNG, WebP — máx. 10MB)</Label>
          <Input
            type="file"
            accept="application/pdf,image/jpeg,image/png,image/webp"
            required
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label>Número</Label>
            <Input value={numero} onChange={(e) => setNumero(e.target.value)} className="font-mono" />
          </div>
          <div>
            <Label>Emissão</Label>
            <Input type="date" value={emissao} onChange={(e) => setEmissao(e.target.value)} />
          </div>
        </div>
        <div>
          <Label>Vencimento (se aplicável)</Label>
          <Input type="date" value={venc} onChange={(e) => setVenc(e.target.value)} />
        </div>
        <Button type="submit" loading={upload.isPending} className="w-full">Enviar para análise</Button>
      </form>
    </AppLayout>
  );
}
