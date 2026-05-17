/** Formatação monetária pt-BR — uso obrigatório em font-mono (Design System). */

const brl = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  minimumFractionDigits: 2,
});

const intl = new Intl.NumberFormat('pt-BR');

export function formatBRL(value: number | string | null | undefined): string {
  if (value == null || value === '') return 'R$ —';
  const n = typeof value === 'string' ? Number(value) : value;
  if (Number.isNaN(n)) return 'R$ —';
  return brl.format(n);
}

export function formatNumber(value: number | string | null | undefined): string {
  if (value == null || value === '') return '—';
  const n = typeof value === 'string' ? Number(value) : value;
  if (Number.isNaN(n)) return '—';
  return intl.format(n);
}

export function centsToBRL(c: number | null | undefined): string {
  if (c == null) return 'R$ —';
  return formatBRL(c / 100);
}

export function maskCPF(raw: string | null | undefined): string {
  if (!raw) return '';
  const d = raw.replace(/\D/g, '').slice(0, 11);
  return d.replace(/(\d{3})(\d{3})(\d{3})(\d{0,2}).*/, (_, a, b, c, e) =>
    e ? `${a}.${b}.${c}-${e}` : `${a}.${b}.${c}`,
  );
}

export function maskCNPJ(raw: string | null | undefined): string {
  if (!raw) return '';
  const d = raw.replace(/\D/g, '').slice(0, 14);
  return d.replace(/(\d{2})(\d{3})(\d{3})(\d{0,4})(\d{0,2}).*/, (_, a, b, c, e, f) => {
    let out = `${a}.${b}.${c}`;
    if (e) out += `/${e}`;
    if (f) out += `-${f}`;
    return out;
  });
}

export function maskCEP(raw: string | null | undefined): string {
  if (!raw) return '';
  const d = raw.replace(/\D/g, '').slice(0, 8);
  return d.replace(/(\d{5})(\d{0,3}).*/, (_, a, b) => (b ? `${a}-${b}` : a));
}

export function maskTelefone(raw: string | null | undefined): string {
  if (!raw) return '';
  const d = raw.replace(/\D/g, '').slice(0, 11);
  if (d.length <= 10) {
    return d.replace(/(\d{2})(\d{0,4})(\d{0,4}).*/, (_, a, b, c) =>
      c ? `(${a}) ${b}-${c}` : b ? `(${a}) ${b}` : `(${a}`,
    );
  }
  return d.replace(/(\d{2})(\d{5})(\d{0,4}).*/, (_, a, b, c) => (c ? `(${a}) ${b}-${c}` : `(${a}) ${b}`));
}
