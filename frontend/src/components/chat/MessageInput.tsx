/**
 * HealthConnect AI - MessageInput Component
 * Chat message input area
 */

'use client';

import { useState, useCallback, type KeyboardEvent, type RefObject } from 'react';
import { Send } from 'lucide-react';
import { CHAT_CONSTANTS } from '@/lib/constants';
import { cn } from '@/lib/utils';

interface MessageInputProps {
  onSend: (content: string) => Promise<void> | void;
  disabled?: boolean;
  placeholder?: string;
  textareaRef?: RefObject<HTMLTextAreaElement>;
  className?: string;
  /** Slot for a streaming toggle or other left-side controls */
  headerSlot?: React.ReactNode;
}

export function MessageInput({
  onSend,
  disabled = false,
  placeholder = 'Write a message…',
  textareaRef,
  className,
  headerSlot,
}: MessageInputProps) {
  const [message, setMessage] = useState('');
  const [isComposing, setIsComposing] = useState(false);

  const handleSend = useCallback(async () => {
    const trimmed = message.trim();
    if (!trimmed || disabled || trimmed.length > CHAT_CONSTANTS.MAX_MESSAGE_LENGTH) return;

    setMessage('');
    await onSend(trimmed);

    // Focus back on textarea
    textareaRef?.current?.focus();
  }, [message, disabled, onSend, textareaRef]);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLTextAreaElement>) => {
      // Send on Enter (without Shift)
      if (event.key === 'Enter' && !event.shiftKey && !isComposing) {
        event.preventDefault();
        handleSend();
      }
    },
    [handleSend, isComposing],
  );

  const characterCount = message.length;
  const isOverLimit = characterCount > CHAT_CONSTANTS.MAX_MESSAGE_LENGTH;

  return (
    <div className={cn('chat-composer px-5 pb-4', className)}>
      {headerSlot && (
        <div className="flex items-center justify-end gap-2 mb-1.5">
          {headerSlot}
        </div>
      )}
      <textarea
        ref={textareaRef}
        data-testid="textarea-chat-message"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        onCompositionStart={() => setIsComposing(true)}
        onCompositionEnd={() => setIsComposing(false)}
        placeholder={placeholder}
        rows={1}
        maxLength={CHAT_CONSTANTS.MAX_MESSAGE_LENGTH + 100}
        disabled={disabled}
        className="w-full resize-none"
        aria-label="Chat message"
      />
      <button
        data-testid="button-send-chat"
        onClick={handleSend}
        disabled={disabled || !message.trim() || isOverLimit}
        aria-label="Send message"
      >
        <Send size={17} />
      </button>

      <div className="flex justify-between mt-1.5 px-1">
        <span className={cn(
          'text-[9px] font-mono',
          isOverLimit ? 'text-destructive' : 'text-muted-foreground/50',
        )}>
          {characterCount}/{CHAT_CONSTANTS.MAX_MESSAGE_LENGTH}
        </span>
        <span className="text-[9px] font-mono text-muted-foreground/50 hidden sm:block">
          Enter to send · Shift+Enter for newline
        </span>
      </div>
    </div>
  );
}