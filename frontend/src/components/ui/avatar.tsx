'use client';

import { type HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

interface AvatarProps extends HTMLAttributes<HTMLDivElement> {
  initials?: string;
  small?: boolean;
  src?: string;
  alt?: string;
}

export function Avatar({ initials = 'HC', small = false, src, alt = '', className, ...props }: AvatarProps) {
  if (src) {
    return (
      <img
        src={src}
        alt={alt || initials}
        className={cn(
          'object-cover',
          small ? 'w-7 h-7 rounded-[9px]' : 'w-[39px] h-[39px] rounded-[13px]',
          'border-2 border-background shadow-[0_0_0_1px_hsl(var(--primary)/.25)]',
          className,
        )}
        {...props as any}
      />
    );
  }

  return (
    <div
      data-testid="img-avatar"
      className={cn(
        'avatar',
        small && 'avatar-small',
        className,
      )}
      {...props}
    >
      <span>{initials}</span>
    </div>
  );
}