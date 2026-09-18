'use client';

import { Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StreamingToggleProps {
  enabled: boolean;
  onChange: (enabled: boolean) => void;
  className?: string;
}

export function StreamingToggle({ enabled, onChange, className }: StreamingToggleProps) {
  return (
    <button
      type="button"
      onClick={() => onChange(!enabled)}
      title={enabled ? 'Streaming enabled — click to disable' : 'Streaming disabled — click to enable'}
      data-testid="button-streaming-toggle"
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-medium transition-colors',
        enabled
          ? 'bg-emerald-100 text-emerald-800 hover:bg-emerald-200'
          : 'bg-slate-100 text-slate-500 hover:bg-slate-200',
        className,
      )}
    >
      <Zap size={11} className={cn(enabled && 'fill-emerald-500 text-emerald-600')} />
      {enabled ? 'Streaming' : 'Standard'}
    </button>
  );
}
