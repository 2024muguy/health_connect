'use client';

import { useState, useRef, useEffect, type ReactNode } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface DropdownItem {
  id: string;
  label: string;
  icon?: ReactNode;
  onClick?: () => void;
  danger?: boolean;
}

interface DropdownProps {
  trigger: ReactNode;
  items: DropdownItem[];
  align?: 'left' | 'right';
  className?: string;
}

export function Dropdown({ trigger, items, align = 'right', className }: DropdownProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={ref} className={cn('relative', className)}>
      <div
        role="button"
        tabIndex={0}
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen(!open)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setOpen(!open);
          }
        }}
        className="flex items-center gap-1 cursor-pointer"
      >
        {trigger}
      </div>
      {open && (
        <div
          className={cn(
            'absolute top-full mt-2 min-w-[160px] rounded-xl border border-border bg-card shadow-xl py-1.5 animate-rise z-50',
            align === 'right' ? 'right-0' : 'left-0',
          )}
        >
          {items.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                item.onClick?.();
                setOpen(false);
              }}
              className={cn(
                'w-full flex items-center gap-2.5 px-4 py-2.5 text-xs font-medium transition-colors text-left',
                item.danger
                  ? 'text-destructive hover:bg-destructive/6'
                  : 'text-foreground hover:bg-muted',
              )}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}