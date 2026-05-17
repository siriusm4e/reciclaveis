import * as React from 'react';
import { cn } from '@/lib/utils';

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = 'text', ...props }, ref) => (
    <input
      type={type}
      ref={ref}
      className={cn(
        'flex h-btn w-full rounded-lg border border-neutral-200 bg-surface-input px-3.5 py-3 text-base font-sans text-neutral-900 placeholder:text-neutral-400 transition-colors duration-base',
        'focus-visible:outline-none focus-visible:border-primary-500 focus-visible:bg-primary-50',
        'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-neutral-100',
        'aria-[invalid=true]:border-error aria-[invalid=true]:bg-error-light/50',
        className,
      )}
      {...props}
    />
  ),
);
Input.displayName = 'Input';
