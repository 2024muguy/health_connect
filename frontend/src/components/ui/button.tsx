'use client';

import { forwardRef, type ButtonHTMLAttributes } from 'react';
import { Loader2, type LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'light' | 'danger';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  fullWidth?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      icon: Icon,
      iconPosition = 'right',
      loading = false,
      fullWidth = false,
      children,
      disabled,
      ...props
    },
    ref,
  ) => {
    const sizeClasses = {
      sm: 'min-h-[32px] px-3 text-[11px] rounded-lg gap-1.5',
      md: 'min-h-[40px] px-4 text-xs rounded-[11px] gap-2',
      lg: 'min-h-[48px] px-6 text-sm rounded-xl gap-2.5',
      icon: 'w-[35px] h-[35px] rounded-[10px] gap-0',
    };

    const variantClasses = {
      primary: 'text-primary-foreground bg-primary hover:shadow-[0_7px_16px_hsl(var(--primary)/.15)]',
      secondary: 'text-foreground border border-border bg-card hover:bg-muted',
      ghost: 'min-h-auto px-0 py-1 text-primary bg-transparent hover:bg-transparent shadow-none',
      light: 'text-sidebar-primary-foreground bg-sidebar-primary',
      danger: 'text-destructive border border-destructive/25 bg-destructive/6 hover:bg-destructive/10',
    };

    return (
      <button
        ref={ref}
        className={cn(
          'button',
          sizeClasses[size],
          variantClasses[variant],
          fullWidth && 'w-full',
          className,
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <Loader2 className="animate-spin" size={size === 'icon' ? 16 : 15} />
        ) : (
          iconPosition === 'left' && Icon && <Icon size={size === 'icon' ? 17 : 15} />
        )}
        {children}
        {iconPosition === 'right' && Icon && !loading && (
          <Icon size={size === 'icon' ? 17 : 15} />
        )}
      </button>
    );
  },
);

Button.displayName = 'Button';

export { Button };