'use client';

import { forwardRef, type HTMLAttributes, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'soft' | 'dark';
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', hover = false, padding = 'md', children, ...props }, ref) => {
    const paddingClasses = {
      none: 'p-0',
      sm: 'p-4',
      md: 'p-[19px]',
      lg: 'p-6',
    };

    const variantClasses = {
      default: 'border border-card-border bg-card',
      soft: 'border border-card-border bg-secondary',
      dark: 'border border-sidebar-border bg-sidebar text-sidebar-foreground',
    };

    return (
      <div
        ref={ref}
        className={cn(
          'rounded-[17px]',
          paddingClasses[padding],
          variantClasses[variant],
          hover && 'transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-lg',
          className,
        )}
        {...props}
      >
        {children}
      </div>
    );
  },
);

Card.displayName = 'Card';

export function CardHeader({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('mb-3', className)} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ className, children, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cn('text-[15px] font-semibold text-foreground', className)} {...props}>
      {children}
    </h3>
  );
}

export function CardDescription({ className, children, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn('text-xs text-muted-foreground leading-relaxed', className)} {...props}>
      {children}
    </p>
  );
}

export function CardContent({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('', className)} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('mt-4 pt-3 border-t border-border', className)} {...props}>
      {children}
    </div>
  );
}

export { Card };