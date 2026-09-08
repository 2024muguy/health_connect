'use client';

import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'card';
}

export function Skeleton({ className, variant = 'rectangular' }: SkeletonProps) {
  const variantClasses = {
    text: 'h-3 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-[14px]',
    card: 'h-28 rounded-[18px]',
  };

  return <div className={cn('skeleton', variantClasses[variant], className)} aria-label="Loading" />;
}

export function SkeletonCard() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-28 w-full" />
      <Skeleton className="h-44 w-full" />
      <Skeleton className="h-24 w-full" />
    </div>
  );
}

export function SkeletonChat() {
  return (
    <div className="space-y-6 py-6">
      <div className="flex gap-3 max-w-[80%]">
        <Skeleton variant="circular" className="w-8 h-8" />
        <Skeleton className="h-16 flex-1" />
      </div>
      <div className="flex gap-3 max-w-[80%] ml-auto flex-row-reverse">
        <Skeleton variant="circular" className="w-8 h-8" />
        <Skeleton className="h-12 flex-1" />
      </div>
      <div className="flex gap-3 max-w-[80%]">
        <Skeleton variant="circular" className="w-8 h-8" />
        <Skeleton className="h-20 flex-1" />
      </div>
    </div>
  );
}