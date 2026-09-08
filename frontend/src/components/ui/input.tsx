'use client';

import { forwardRef, type InputHTMLAttributes, type TextareaHTMLAttributes } from 'react';
import { Search, type LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: LucideIcon;
  helperText?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, icon: Icon, helperText, id, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={id}
            className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground"
          >
            {label}
          </label>
        )}
        <div className="relative">
          {Icon && (
            <Icon
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
          )}
          <input
            ref={ref}
            id={id}
            className={cn(
              'w-full h-[43px] px-3 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none transition-all',
              'focus:border-primary focus:ring-[3px] focus:ring-primary/12',
              Icon && 'pl-10',
              error && 'border-destructive focus:border-destructive focus:ring-destructive/12',
              className,
            )}
            aria-invalid={!!error}
            {...props}
          />
        </div>
        {error ? (
          <p className="mt-1.5 text-[10px] text-destructive">{error}</p>
        ) : helperText ? (
          <p className="mt-1.5 text-[10px] text-muted-foreground">{helperText}</p>
        ) : null}
      </div>
    );
  },
);

Input.displayName = 'Input';

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, helperText, id, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={id}
            className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground"
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={id}
          className={cn(
            'w-full px-3 py-3 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none transition-all resize-vertical',
            'focus:border-primary focus:ring-[3px] focus:ring-primary/12',
            error && 'border-destructive',
            className,
          )}
          aria-invalid={!!error}
          {...props}
        />
        {error ? (
          <p className="mt-1.5 text-[10px] text-destructive">{error}</p>
        ) : helperText ? (
          <p className="mt-1.5 text-[10px] text-muted-foreground">{helperText}</p>
        ) : null}
      </div>
    );
  },
);

Textarea.displayName = 'Textarea';

export interface SearchFieldProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export function SearchField({ value, onChange, placeholder = 'Search', className }: SearchFieldProps) {
  return (
    <label className={cn(
      'search-field',
      'flex items-center gap-2 h-[34px] px-3 rounded-[9px] border border-border text-muted-foreground',
      className,
    )}>
      <Search size={16} />
      <input
        data-testid="input-search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="flex-1 h-full border-0 bg-transparent text-xs outline-none shadow-none focus:ring-0"
      />
      <kbd className="hidden md:block text-[8px] font-mono text-muted-foreground">⌘ K</kbd>
    </label>
  );
}

export { Input, Textarea };