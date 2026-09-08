'use client';

import { type HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'neutral';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  dot?: boolean;
  size?: 'sm' | 'md';
}

export function Badge({ variant = 'default', dot = false, size = 'sm', className, children, ...props }: BadgeProps) {
  const sizeClasses = {
    sm: 'px-1.5 py-0.5 text-[8px]',
    md: 'px-2.5 py-1 text-[10px]',
  };

  const variantClasses: Record<BadgeVariant, string> = {
    default: 'bg-muted text-muted-foreground',
    primary: 'bg-primary/10 text-primary',
    success: 'bg-primary/14 text-[hsl(166_40%_29%)]',
    warning: 'bg-accent/18 text-[hsl(32_66%_37%)]',
    danger: 'bg-destructive/10 text-destructive',
    neutral: 'bg-secondary text-secondary-foreground',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-md font-mono font-bold uppercase tracking-wider',
        sizeClasses[size],
        variantClasses[variant],
        className,
      )}
      {...props}
    >
      {dot && <span className="w-1 h-1 rounded-full bg-current" />}
      {children}
    </span>
  );
}

export type StatusVariant = 'confirmed' | 'pending' | 'completed' | 'cancelled' | 'scheduled';

export function StatusPill({ status, className }: { status?: string; className?: string }) {
  const label = status ? status[0].toUpperCase() + status.slice(1) : 'Unknown';
  const statusClass = `status-${status || 'completed'}`;

  return (
    <span
      data-testid={`status-${status}`}
      className={cn('status-pill', statusClass, className)}
    >
      <span className="status-dot" />
      {label}
    </span>
  );
}