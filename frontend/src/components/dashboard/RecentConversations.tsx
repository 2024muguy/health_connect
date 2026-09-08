/**
 * HealthConnect AI - RecentConversations Component
 * Display recent AI assistant conversations
 */

'use client';

import Link from 'next/link';
import { MessageCircle, ArrowRight } from 'lucide-react';
import type { Conversation } from '@/types';
import { formatRelative } from '@/lib/utils';
import { EmptyState } from '@/components/shared/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';

interface RecentConversationsProps {
  conversations: Conversation[];
  isLoading?: boolean;
  maxItems?: number;
  className?: string;
}

export function RecentConversations({
  conversations,
  isLoading = false,
  maxItems = 5,
  className,
}: RecentConversationsProps) {
  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-[52px] w-full" />
        ))}
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <EmptyState
        icon={MessageCircle}
        title="No conversations yet"
        text="Start a conversation with your care assistant for help with appointments, services, and more."
        action={
          <Link
            href="/chat"
            className="button button-primary"
          >
            Start conversation
            <ArrowRight size={15} />
          </Link>
        }
      />
    );
  }

  return (
    <div className={`conversation-preview-grid ${className || ''}`}>
      {conversations.slice(0, maxItems).map((conversation) => (
        <Link
          key={conversation.id}
          href={`/chat/${conversation.id}`}
          data-testid={`link-conversation-${conversation.id}`}
          className="conversation-row"
        >
          <div className="conversation-icon">
            <MessageCircle size={17} />
          </div>
          <div className="min-w-0 flex-1">
            <div className="conversation-title">
              {conversation.title || 'Conversation'}
            </div>
            <p>{conversation.preview || 'No messages yet'}</p>
          </div>
          <div className="conversation-time">
            {formatRelative(conversation.updatedAt)}
          </div>
          <ArrowRight size={15} className="row-arrow" />
        </Link>
      ))}
    </div>
  );
}