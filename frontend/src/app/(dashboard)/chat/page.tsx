/**
 * HealthConnect AI - Chat Hub Page
 * Conversation list and new chat composer
 */

'use client';

import { useState, useMemo, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { Sparkles, Send, Search, MessageCircle } from 'lucide-react';
import { useChat } from '@/hooks/useChat';
import { SearchField } from '@/components/ui/input';
import { EmptyState } from '@/components/shared/EmptyState';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { Skeleton } from '@/components/ui/skeleton';
import { CHAT_CONSTANTS } from '@/lib/constants';
import { cn } from '@/lib/utils';

export default function ChatPage() {
  const router = useRouter();
  const {
    conversations,
    isSending,
    error,
    sendMessage,
    loadConversations,
    deleteConversation,
  } = useChat();

  const [search, setSearch] = useState('');
  const [newMessage, setNewMessage] = useState('');
  const [showNewChat, setShowNewChat] = useState(false);

  const filteredConversations = useMemo(() => {
    return conversations.filter((conversation) => {
      const searchable = `${conversation.title || ''} ${conversation.preview || ''}`.toLowerCase();
      return searchable.includes(search.toLowerCase());
    });
  }, [conversations, search]);

  const handleNewChat = async (event: FormEvent) => {
    event.preventDefault();
    if (!newMessage.trim()) return;

    try {
      const response = await sendMessage(newMessage.trim());
      const convId = (response as any)?.conversation_id ?? (response as any)?.conversationId;
      if (convId) {
        router.push(`/chat/${convId}`);
      }
    } catch {
      // Error handled by hook
    }
  };

  return (
    <>
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
        <div>
          <p className="eyebrow">Your care assistant</p>
          <h1 className="page-title">Conversations</h1>
          <p className="mt-2 text-sm text-muted-foreground max-w-xl">
            A private space for clear answers and next steps.
          </p>
        </div>
        <div className="assistant-availability">
          <span />
          Usually replies in a moment
        </div>
      </div>

      {showNewChat ? (
        <div className="max-w-3xl">
          <ChatInterface onNewConversation={() => setShowNewChat(false)} />
        </div>
      ) : (
        <div className="chat-hub">
          {/* Conversation List */}
          <section className="conversation-list-panel">
            <div className="panel-toolbar">
              <strong>Recent conversations</strong>
              <SearchField
                value={search}
                onChange={setSearch}
                placeholder="Search conversations"
              />
            </div>

            {filteredConversations.length > 0 ? (
              <div>
                {filteredConversations.map((conversation) => (
                  <button
                    key={conversation.id}
                    onClick={() => router.push(`/chat/${conversation.id}`)}
                    className="conversation-row w-full text-left"
                    data-testid={`link-conversation-${conversation.id}`}
                  >
                    <div className="conversation-icon">
                      <MessageCircleIcon size={17} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="conversation-title">
                        {conversation.title || 'Conversation'}
                      </div>
                      <p>{conversation.preview || 'No messages yet'}</p>
                    </div>
                    <span className="conversation-time">
                      {conversation.updatedAt ? formatRelative(conversation.updatedAt) : ''}
                    </span>
                  </button>
                ))}
              </div>
            ) : search ? (
              <EmptyState
                icon={Search}
                title="No conversations found"
                text="Try a different search term."
              />
            ) : (
              <EmptyState
                title="No conversations yet"
                text="Start a conversation when you need a hand with appointments, services, or visit preparation."
              />
            )}
          </section>

          {/* New Chat Panel */}
          <section className="new-chat-panel">
            <div className="new-chat-orb">
              <Sparkles size={22} />
            </div>
            <p className="eyebrow">START FRESH</p>
            <h2>What is on your mind?</h2>
            <p>
              Ask about a visit, a service, or anything you would like to
              understand better.
            </p>

            <form onSubmit={handleNewChat} className="new-chat-composer">
              <textarea
                data-testid="textarea-new-chat"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your question…"
                rows={3}
                maxLength={CHAT_CONSTANTS.MAX_MESSAGE_LENGTH}
              />
              <button
                data-testid="button-send-new-chat"
                disabled={isSending || !newMessage.trim()}
                aria-label="Send message"
              >
                <Send size={17} />
              </button>
            </form>

            <div className="suggestion-row">
              {CHAT_CONSTANTS.SUGGESTIONS.slice(0, 2).map((suggestion, index) => (
                <button
                  key={index}
                  data-testid={`button-suggestion-${index}`}
                  onClick={() => setNewMessage(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </section>
        </div>
      )}
    </>
  );
}

// Helper components
function MessageCircleIcon({ size }: { size: number }) {
  return <MessageCircle size={size} />;
}

function formatRelative(date: string): string {
  const diff = Date.now() - new Date(date).getTime();
  const minutes = Math.max(1, Math.floor(diff / 60000));
  if (minutes < 60) return `${minutes}m ago`;
  if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
  return `${Math.floor(minutes / 1440)}d ago`;
}