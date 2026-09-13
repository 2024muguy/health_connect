'use client';

import * as React from 'react';
import { Loader2, type LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

/* ============================================================
   Base Button
   ============================================================ */

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'link';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  leftIcon?: LucideIcon;
  rightIcon?: LucideIcon;
  fullWidth?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'default',
      size = 'md',
      leftIcon: LeftIcon,
      rightIcon: RightIcon,
      fullWidth,
      children,
      ...props
    },
    ref
  ) => {
    const variants: Record<NonNullable<ButtonProps['variant']>, string> = {
      default: 'bg-primary text-primary-foreground hover:bg-primary/90',
      secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
      outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
      ghost: 'hover:bg-accent hover:text-accent-foreground',
      destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
      link: 'text-primary underline-offset-4 hover:underline',
    };

    const sizes: Record<NonNullable<ButtonProps['size']>, string> = {
      sm: 'h-8 px-3 text-xs',
      md: 'h-10 px-4 text-sm',
      lg: 'h-12 px-6 text-base',
      icon: 'h-10 w-10',
    };

    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center gap-2 rounded-[10px] font-medium transition-colors',
          'focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-primary/20',
          'disabled:pointer-events-none disabled:opacity-60',
          variants[variant],
          sizes[size],
          fullWidth && 'w-full',
          className
        )}
        {...props}
      >
        {LeftIcon && <LeftIcon size={size === 'sm' ? 14 : 16} />}
        {children}
        {RightIcon && <RightIcon size={size === 'sm' ? 14 : 16} />}
      </button>
    );
  }
);
Button.displayName = 'Button';

/* ============================================================
   Loading Button
   ============================================================ */

export interface LoadingButtonProps extends ButtonProps {
  loading?: boolean;
  loadingText?: string;
}

export const LoadingButton = React.forwardRef<
  HTMLButtonElement,
  LoadingButtonProps
>(
  (
    { loading, loadingText, children, disabled, leftIcon, rightIcon, ...props },
    ref
  ) => (
    <Button
      ref={ref}
      disabled={disabled || loading}
      leftIcon={loading ? Loader2 : leftIcon}
      rightIcon={loading ? undefined : rightIcon}
      {...props}
    >
      {loading ? loadingText || children : children}
    </Button>
  )
);
LoadingButton.displayName = 'LoadingButton';

/* ============================================================
   Icon Button
   ============================================================ */

export interface IconButtonProps extends ButtonProps {
  icon: LucideIcon;
  'aria-label': string;
}

export const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ icon: Icon, size = 'icon', className, ...props }, ref) => (
    <Button
      ref={ref}
      size={size}
      className={cn('p-0', className)}
      {...props}
    >
      <Icon size={16} />
    </Button>
  )
);
IconButton.displayName = 'IconButton';
