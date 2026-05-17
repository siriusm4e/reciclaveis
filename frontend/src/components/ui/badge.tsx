import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center font-sans font-bold uppercase tracking-wider rounded-full text-[10px] leading-none px-[11px] py-[4px]',
  {
    variants: {
      variant: {
        neutral: 'bg-neutral-100 text-neutral-600',
        primary: 'bg-primary-100 text-primary-700',
        accent: 'bg-accent-500/20 text-accent-600',
        success: 'bg-success-light text-success-dark',
        warning: 'bg-warning-light text-warning-dark',
        error: 'bg-error text-neutral-0',
        info: 'bg-info-light text-info-dark',
      },
    },
    defaultVariants: { variant: 'neutral' },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
