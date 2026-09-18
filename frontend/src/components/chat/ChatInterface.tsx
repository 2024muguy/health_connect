/**
 * HealthConnect AI - ChatInterface Component
 * Main chat interface combining all chat components
 */

'use client';

import { useRef, useEffect, useCallback } from 'react';
import { useChat } from '@/hooks/useChat';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';
import { TypingIndicator } from './TypingIndicator';
import { ChatHeader } from './ChatHeader';
import { QuickReplies } from './QuickReplies';
import { EmptyState } from '@/components/shared/EmptyState';
import { MessageCircle } from 'lucide-react';
import { CHAT_CONSTANTS } from '@/lib/constants';
import { cn } from '@/lib/utils';

interface ChatInterfaceProps {
  onNewConversation?: () => void;
  onDelete?: () => Promise<void>;
  conversationId?: string;
  patientName?: string;
  className?: string;
}

export function ChatInterface({
  conversationId,
  patientName,
  className,
}: ChatInterfaceProps) {
  const {
    messages,
    isSending,
    isStreaming,
    connectionStatus,
    error,
    sendMessage,
    setActiveConversation,
  } = useChat(conversationId);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  const handleSend = useCallback(
    async (content: string) => {
      await sendMessage(content, conversationId);
    },
    [sendMessage, conversationId],
  );

  const handleQuickReply = useCallback(
    (reply: string) => {
      handleSend(reply);
    },
    [handleSend],
  );

  const isConnected = connectionStatus === 'connected';

  return (
    <div
      className={cn(
        'flex flex-col h-full bg-card rounded-[18px] border border-card-border shadow-sm overflow-hidden',
        className,
      )}
    >
      <ChatHeader
        conversationId={conversationId}
        patientName={patientName}
        connectionStatus={connectionStatus}
      />

      <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-background/30">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <EmptyState
              icon={MessageCircle}
              title="Welcome to HealthConnect AI"
              text="How can I help you today? Ask about appointments, services, or preparing for your visit."
            />
          </div>
        ) : (
          messages.map((message, index) => (
            <MessageBubble
              key={message.id || index}
              message={message}
              isStreaming={isStreaming && index === messages.length - 1}
            />
          ))
        )}

        {(isSending || isStreaming) && <TypingIndicator />}

        {error && (
          <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-xl text-xs">
            {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {messages.length === 0 && !isSending && (
        <div className="px-5 pb-3">
          <QuickReplies
            replies={[...CHAT_CONSTANTS.QUICK_REPLIES]}
            onReply={handleQuickReply}
            disabled={false}
          />
        </div>
      )}

      <MessageInput
        onSend={handleSend}
        disabled={isSending}
        textareaRef={textareaRef}
      />

      <p className="disclaimer px-5 pb-2">
        HealthConnect AI shares general information, not a diagnosis. For urgent concerns, call the clinic directly.
      </p>
    </div>
  );
}