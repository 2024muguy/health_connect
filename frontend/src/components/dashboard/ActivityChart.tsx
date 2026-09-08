/**
 * HealthConnect AI - ActivityChart Component
 * Simple activity visualization chart
 */

'use client';

import { useMemo } from 'react';
import { cn } from '@/lib/utils';

interface ActivityDataPoint {
  label: string;
  value: number;
  date?: string;
}

interface ActivityChartProps {
  data: ActivityDataPoint[];
  height?: number;
  className?: string;
  color?: 'primary' | 'accent';
}

export function ActivityChart({
  data,
  height = 120,
  className,
  color = 'primary',
}: ActivityChartProps) {
  const maxValue = useMemo(() => {
    return Math.max(...data.map((d) => d.value), 1);
  }, [data]);

  const barColor = color === 'primary' ? 'bg-primary' : 'bg-accent';
  const hoverColor = color === 'primary' ? 'hover:bg-primary/80' : 'hover:bg-accent/80';

  if (data.length === 0) {
    return (
      <div className={cn('flex items-center justify-center', className)} style={{ height }}>
        <p className="text-xs text-muted-foreground">No activity data yet</p>
      </div>
    );
  }

  return (
    <div className={cn('flex items-end gap-2', className)} style={{ height }}>
      {data.map((point, index) => {
        const barHeight = (point.value / maxValue) * 100;
        
        return (
          <div
            key={index}
            className="flex-1 flex flex-col items-center gap-1.5 group"
          >
            <div className="relative w-full flex items-end justify-center" style={{ height: height - 30 }}>
              <div
                className={cn(
                  'w-full max-w-[28px] rounded-t-md transition-all duration-300 group-hover:opacity-80',
                  barColor,
                  hoverColor,
                )}
                style={{ height: `${Math.max(barHeight, 2)}%` }}
                title={`${point.label}: ${point.value}`}
              />
              {/* Tooltip */}
              <div className="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 rounded-md bg-foreground text-background text-[9px] font-medium opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                {point.value}
              </div>
            </div>
            <span className="text-[8px] font-mono text-muted-foreground truncate max-w-full">
              {point.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}