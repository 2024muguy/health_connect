/**
 * HealthConnect AI - Conversation Detail Page
 */

'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { useChat } from '@/hooks/useChat';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { useToast } from '@/hooks/useToast';

export default function ConversationPage() {
  const params = useParams();
  const router = useRouter();
  const conversationId = params?.conversationId as string;
  const { toast } = useToast();

  const {
    loadConversation,
    deleteConversation,
    isLoading,
  } = useChat(conversationId);

  useEffect(() => {
    if (conversationId) {
      loadConversation(conversationId);
    }
  }, [conversationId, loadConversation]);

  const handleDelete = async () => {
    if (!window.confirm('Delete this conversation?')) return;

    try {
      await deleteConversation(conversationId);
      toast('Conversation deleted.', 'success');
      router.push('/chat');
    } catch {
      toast('Failed to delete conversation.', 'error');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
        <LoadingSpinner size="lg" label="Loading conversation…" />
      </div>
    );
  }

  return (
    <>
      <Link
        href="/chat"
        className="back-link"
        data-testid="link-back"
      >
        <ArrowLeft size={15} />
        Back to conversations
      </Link>

      <div className="max-w-[790px] mx-auto">
        <ChatInterface
          conversationId={conversationId}
          onDelete={handleDelete}
        />
      </div>
    </>
  );
}