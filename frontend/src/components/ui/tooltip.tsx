'use client';

import { createContext, useContext, useState, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface TooltipContextValue {
  showTooltip: (content: string, target: HTMLElement) => void;
  hideTooltip: () => void;
}

const TooltipContext = createContext<TooltipContextValue | null>(null);

export function useTooltip() {
  const context = useContext(TooltipContext);
  if (!context) throw new Error('useTooltip must be used within TooltipProvider');
  return context;
}

export function TooltipProvider({ children }: { children: ReactNode }) {
  const [tooltip, setTooltip] = useState<{ content: string; x: number; y: number } | null>(null);

  const showTooltip = (content: string, target: HTMLElement) => {
    const rect = target.getBoundingClientRect();
    setTooltip({
      content,
      x: rect.left + rect.width / 2,
      y: rect.top - 8,
    });
  };

  const hideTooltip = () => setTooltip(null);

  return (
    <TooltipContext.Provider value={{ showTooltip, hideTooltip }}>
      {children}
      {tooltip && (
        <div
          className="fixed z-50 px-2.5 py-1.5 rounded-lg bg-foreground text-background text-[10px] font-medium pointer-events-none -translate-x-1/2 -translate-y-full shadow-lg"
          style={{ left: tooltip.x, top: tooltip.y }}
        >
          {tooltip.content}
        </div>
      )}
    </TooltipContext.Provider>
  );
}