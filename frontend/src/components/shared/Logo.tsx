'use client';

import { HeartPulse } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LogoProps {
  variant?: 'sidebar' | 'topbar' | 'landing';
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  className?: string;
}

export function Logo({ variant = 'sidebar', size = 'md', showText = true, className }: LogoProps) {
  const sizeClasses = {
    sm: { mark: 'w-6 h-6 rounded-lg', text: 'text-xs', sub: 'text-[8px]', icon: 14 },
    md: { mark: 'w-[34px] h-[34px] rounded-[11px]', text: 'text-[15px]', sub: 'text-[10px]', icon: 19 },
    lg: { mark: 'w-12 h-12 rounded-2xl', text: 'text-xl', sub: 'text-xs', icon: 26 },
  };

  const current = sizeClasses[size];

  if (variant === 'landing') {
    return (
      <div className={cn('flex flex-col items-center', className)}>
        <div className={cn(
          'grid place-items-center',
          current.mark,
          'bg-primary text-primary-foreground',
        )}>
          <HeartPulse size={current.icon} strokeWidth={2.5} />
        </div>
        {showText && (
          <div className="mt-3 text-center">
            <div className={cn('font-bold text-foreground', current.text)}>HealthConnect</div>
            <div className={cn('text-muted-foreground uppercase tracking-wider mt-0.5 font-mono', current.sub)}>
              Patient Companion
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={cn('flex items-center gap-[11px]', className)}>
      <div className={cn(
        'grid place-items-center',
        current.mark,
        variant === 'sidebar'
          ? 'bg-sidebar-primary text-sidebar-primary-foreground -rotate-[7deg]'
          : 'bg-primary text-primary-foreground',
      )}>
        <HeartPulse size={current.icon} strokeWidth={2.5} />
      </div>
      {showText && (
        <div>
          <div className={cn(
            'font-bold leading-tight',
            variant === 'sidebar' ? 'text-sidebar-foreground' : 'text-foreground',
            current.text,
          )}>
            HealthConnect
          </div>
          <div className={cn(
            'mt-0.5 uppercase tracking-wider font-mono',
            variant === 'sidebar' ? 'text-sidebar-foreground/54' : 'text-muted-foreground',
            current.sub,
          )}>
            patient companion
          </div>
        </div>
      )}
    </div>
  );
}