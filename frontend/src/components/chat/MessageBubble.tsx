/**
 * HealthConnect AI - MessageBubble Component
 * Individual chat message bubble
 */

'use client';

import { Sparkles, FileText } from 'lucide-react';
import type { ChatMessage } from '@/types';
import { cn, formatTime } from '@/lib/utils';

interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
  className?: string;
}

export function MessageBubble({ message, isStreaming = false, className }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';
  const citations = message.citations ?? [];

  return (
    <div
      data-testid={`message-${message.id}`}
      className={cn(
        'message',
        isUser && 'user-message',
        isAssistant && 'assistant-message',
        className,
      )}
    >
      <div className="message-avatar">
        {isAssistant ? <Sparkles size={14} /> : 'ME'}
      </div>

      <div className="min-w-0">
        <div
          className={cn(
            'message-content',
            isStreaming && 'animate-pulse',
          )}
        >
          {message.content}
          {isStreaming && <span className="inline-block w-1.5 h-4 bg-current ml-0.5 animate-pulse" />}
        </div>

        <span className="message-time">
          {formatTime(message.timestamp)}
        </span>

        {process.env.NODE_ENV === 'development' && false && citations.length > 0 && (
          <div className="citations">
            {citations.map((citation, index) => (
              <span key={index}>
                <FileText size={12} />
                {citation.formatted || citation.chunk_id}
              </span>
            ))}
          </div>
        )}

        {process.env.NODE_ENV === 'development' && false && message.intent && isAssistant && (
          <span className="text-[8px] font-mono text-muted-foreground/60 mt-1 block">
            intent: {message.intent}
          </span>
        )}
      </div>
    </div>
  );
}