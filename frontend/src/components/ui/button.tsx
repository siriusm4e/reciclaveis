import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';

import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap font-sans font-bold text-base rounded-xl transition-colors duration-base ease-base disabled:pointer-events-none disabled:opacity-50 tap-target focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-background',
  {
    variants: {
      variant: {
        primary:
          'bg-primary-500 text-neutral-0 shadow-primary hover:bg-primary-600 active:bg-primary-700',
        accent:
          'bg-accent-500 text-neutral-0 shadow-accent hover:bg-accent-600',
        secondary:
          'bg-neutral-0 text-primary-700 border border-neutral-200 hover:bg-primary-50 hover:border-primary-500',
        outline:
          'bg-transparent text-neutral-900 border border-neutral-300 hover:bg-neutral-50',
        ghost: 'bg-transparent text-neutral-700 hover:bg-neutral-100',
        danger:
          'bg-error text-neutral-0 hover:bg-error-dark shadow-sm',
        link: 'bg-transparent text-primary-700 underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-btn px-5',
        sm: 'h-tap px-4 text-sm',
        lg: 'h-14 px-6 text-lg',
        icon: 'h-tap w-tap p-0',
      },
    },
    defaultVariants: { variant: 'primary', size: 'default' },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, loading = false, disabled, children, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp
        className={cn(buttonVariants({ variant, size }), className)}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-r-transparent" />
        )}
        {children}
      </Comp>
    );
  },
);
Button.displayName = 'Button';
