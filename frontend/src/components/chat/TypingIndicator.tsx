/**
 * HealthConnect AI - TypingIndicator Component
 * Animated typing indicator for AI assistant
 */

'use client';

import { Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TypingIndicatorProps {
  className?: string;
}

export function TypingIndicator({ className }: TypingIndicatorProps) {
  return (
    <div
      className={cn('message assistant-message', className)}
      data-testid="typing-indicator"
      aria-label="Assistant is typing"
    >
      <div className="message-avatar">
        <Sparkles size={14} />
      </div>
      <div className="message-content flex items-center gap-1.5 py-3">
        <div className="thinking flex gap-1">
          <span />
          <span />
          <span />
        </div>
      </div>
    </div>
  );
}