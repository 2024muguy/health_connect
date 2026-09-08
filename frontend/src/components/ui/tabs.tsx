'use client';

import { type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface TabItem {
  id: string;
  label: string;
  count?: number;
  content?: ReactNode;
}

interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  variant?: 'segmented' | 'underline';
  className?: string;
}

export function Tabs({ tabs, activeTab, onTabChange, variant = 'segmented', className }: TabsProps) {
  if (variant === 'segmented') {
    return (
      <div className={cn('inline-flex p-1 rounded-[10px] bg-muted', className)}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            data-testid={`button-tab-${tab.id}`}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              'px-3.5 py-2 rounded-[7px] text-[11px] transition-all',
              activeTab === tab.id
                ? 'bg-card text-foreground font-bold shadow-[0_2px_6px_hsl(190_20%_30%/.08)]'
                : 'text-muted-foreground hover:text-foreground',
            )}
          >
            {tab.label}
            {tab.count !== undefined && (
              <span className="ml-1.5 text-[9px] font-mono text-muted-foreground">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className={cn('flex gap-1 border-b border-border', className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={cn(
            'px-4 py-2.5 text-xs font-medium border-b-2 -mb-px transition-colors',
            activeTab === tab.id
              ? 'border-primary text-primary font-semibold'
              : 'border-transparent text-muted-foreground hover:text-foreground',
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}