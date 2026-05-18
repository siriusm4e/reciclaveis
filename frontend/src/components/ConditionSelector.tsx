/**
 * ConditionSelector — botões de seleção única (toggle) para um grupo de Condição.
 *
 * Cada grupo (limpeza / umidade / forma) só admite UM valor selecionado por vez.
 * Clicar no valor já selecionado limpa a seleção (volta a null) — útil em filtros.
 */

import { cn } from '@/lib/utils';
import type { CondicaoForma, CondicaoLimpeza, CondicaoUmidade } from '@/types/api';

export type CondicaoGroup = 'limpeza' | 'umidade' | 'forma';

type ValueForGroup = {
  limpeza: CondicaoLimpeza;
  umidade: CondicaoUmidade;
  forma: CondicaoForma;
};

const OPTIONS: Record<CondicaoGroup, Array<{ value: string; label: string }>> = {
  limpeza: [
    { value: 'limpo', label: 'Limpo' },
    { value: 'sujo', label: 'Sujo' },
    { value: 'contaminado', label: 'Contaminado' },
  ],
  umidade: [
    { value: 'seco', label: 'Seco' },
    { value: 'umido', label: 'Úmido' },
    { value: 'molhado', label: 'Molhado' },
  ],
  forma: [
    { value: 'solto', label: 'Solto' },
    { value: 'fardo', label: 'Fardo' },
    { value: 'prensado', label: 'Prensado' },
    { value: 'moido', label: 'Moído' },
    { value: 'triturado', label: 'Triturado' },
    { value: 'granulado', label: 'Granulado' },
  ],
};

const LABEL_GROUP: Record<CondicaoGroup, string> = {
  limpeza: 'Limpeza',
  umidade: 'Umidade',
  forma: 'Forma',
};

export interface ConditionSelectorProps<G extends CondicaoGroup> {
  group: G;
  value: ValueForGroup[G] | null;
  onChange: (v: ValueForGroup[G] | null) => void;
  /** Esconde o rótulo do grupo (use quando você renderiza um Label externo) */
  hideGroupLabel?: boolean;
  /** Permite limpar a seleção clicando no item ativo (default true em filtros) */
  allowClear?: boolean;
  className?: string;
}

export function ConditionSelector<G extends CondicaoGroup>({
  group,
  value,
  onChange,
  hideGroupLabel = false,
  allowClear = true,
  className,
}: ConditionSelectorProps<G>) {
  const opts = OPTIONS[group];

  return (
    <div className={cn('space-y-1.5', className)}>
      {!hideGroupLabel && (
        <p className="text-xs font-semibold text-neutral-700">{LABEL_GROUP[group]}</p>
      )}
      <div className="flex flex-wrap gap-1.5" role="radiogroup" aria-label={LABEL_GROUP[group]}>
        {opts.map((opt) => {
          const active = value === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              role="radio"
              aria-checked={active}
              onClick={() => {
                if (active && allowClear) {
                  onChange(null);
                } else {
                  onChange(opt.value as ValueForGroup[G]);
                }
              }}
              className={cn(
                'rounded-full border px-3 py-1 text-xs font-medium transition-colors duration-base',
                active
                  ? 'border-primary-500 bg-primary-500 text-white'
                  : 'border-neutral-200 bg-surface-card text-neutral-700 hover:border-primary-300',
              )}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
