'use client';

import { type ReactNode } from 'react';
import { CalendarDays, type LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  text: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({
  icon: Icon = CalendarDays,
  title,
  text,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div className={cn('empty-panel py-12', className)}>
      <div className="empty-icon">
        <Icon size={21} />
      </div>
      <h3>{title}</h3>
      <p>{text}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}