/**
 * HealthConnect AI - QuickReplies Component
 * Quick reply suggestion buttons
 */

'use client';

import { cn } from '@/lib/utils';

interface QuickRepliesProps {
  replies: string[];
  onReply: (reply: string) => void;
  disabled?: boolean;
  className?: string;
}

export function QuickReplies({
  replies,
  onReply,
  disabled = false,
  className,
}: QuickRepliesProps) {
  if (replies.length === 0) return null;

  return (
    <div className={cn('suggestion-row', className)}>
      {replies.map((reply, index) => (
        <button
          key={index}
          data-testid={`button-quick-reply-${index}`}
          onClick={() => onReply(reply)}
          disabled={disabled}
          className="hover-elevate"
        >
          {reply}
        </button>
      ))}
    </div>
  );
}