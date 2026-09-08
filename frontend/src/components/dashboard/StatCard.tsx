/**
 * HealthConnect AI - StatCard Component
 * Dashboard statistics card
 */

'use client';

import { type LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatCardProps {
  label: string;
  value: number | string;
  icon?: LucideIcon;
  trend?: number;
  trendLabel?: string;
  variant?: 'default' | 'primary' | 'accent';
  className?: string;
}

export function StatCard({
  label,
  value,
  icon: Icon,
  trend,
  trendLabel,
  variant = 'default',
  className,
}: StatCardProps) {
  const variantClasses = {
    default: 'bg-card border-card-border',
    primary: 'bg-primary/10 border-primary/20',
    accent: 'bg-accent/10 border-accent/20',
  };

  return (
    <div
      className={cn(
        'rounded-[17px] border p-5',
        variantClasses[variant],
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[9px] font-mono uppercase tracking-[0.1em] text-muted-foreground">
            {label}
          </p>
          <p className="mt-3 font-serif text-[28px] leading-none text-foreground">
            {value}
          </p>
        </div>
        {Icon && (
          <div className="w-9 h-9 rounded-[12px] bg-primary/10 grid place-items-center">
            <Icon size={18} className="text-primary" />
          </div>
        )}
      </div>

      {trend !== undefined && (
        <div className="mt-4 flex items-center gap-2 pt-3 border-t border-border">
          {trend >= 0 ? (
            <TrendingUp size={14} className="text-primary" />
          ) : (
            <TrendingDown size={14} className="text-destructive" />
          )}
          <span
            className={cn(
              'text-[10px] font-semibold',
              trend >= 0 ? 'text-primary' : 'text-destructive',
            )}
          >
            {trend >= 0 ? '+' : ''}
            {trend}%
          </span>
          {trendLabel && (
            <span className="text-[10px] text-muted-foreground">{trendLabel}</span>
          )}
        </div>
      )}
    </div>
  );
}