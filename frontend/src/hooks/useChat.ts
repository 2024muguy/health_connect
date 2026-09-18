/**
 * HealthConnect AI - useChat Hook
 * Chat logic with WebSocket streaming support
 */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { chatApi } from '@/lib/api';
import { WebSocketClient, type WebSocketStatus, type WebSocketMessage } from '@/lib/websocket';
import { useChatStore } from '@/stores/chat-store';
import type { ChatMessage, ChatResponse, Conversation } from '@/types';
import { CHAT_CONSTANTS } from '@/lib/constants';

interface UseChatReturn {
  isLoading: boolean;
  messages: ChatMessage[];
  conversations: Conversation[];
  activeConversationId: string | null;
  isSending: boolean;
  isStreaming: boolean;
  connectionStatus: WebSocketStatus;
  error: string | null;
  sendMessage: (content: string, conversationId?: string) => Promise<ChatResponse | undefined>;
  loadConversations: () => Promise<void>;
  loadConversation: (id: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  setActiveConversation: (id: string | null) => void;
  clearError: () => void;
}

export function useChat(initialConversationId?: string): UseChatReturn {
  const {
    conversations,
    activeConversationId,
    messages,
    isStreaming,
    setActiveConversation,
    addConversation,
    updateConversation,
    removeConversation,
    addMessage,
    addMessages,
    clearMessages,
    setStreaming,
    setTypingIndicator,
  } = useChatStore();

  const [isSending, setIsSending] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<WebSocketStatus>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocketClient | null>(null);

  // Initialize WebSocket connection for streaming
  useEffect(() => {
    if (!initialConversationId && !activeConversationId) return;

    const conversationId = initialConversationId || activeConversationId;
    if (!conversationId) return;

    const ws = WebSocketClient.getInstance(conversationId, {
      onMessage: handleWebSocketMessage,
      onStatusChange: setConnectionStatus,
      onError: (err) => setError(err.message),
    });

    // Attach the current access token BEFORE connecting so the
    // handshake URL carries ?token=...
    if (typeof window !== 'undefined') {
      const token = window.localStorage.getItem('hc_access_token');
      if (token) ws.setToken(token);
    }

    ws.connect();
    wsRef.current = ws;

    return () => {
      ws.disconnect();
      wsRef.current = null;
    };
  }, [initialConversationId, activeConversationId]);

  const handleWebSocketMessage = useCallback(
    (message: WebSocketMessage) => {
      if (message.type === 'chunk' && message.content) {
        setStreaming(true);
        // Update last assistant message with streamed chunk
        const conversationId = activeConversationId || initialConversationId;
        if (conversationId) {
          const currentMessages = messages[conversationId] || [];
          const lastMessage = currentMessages[currentMessages.length - 1];

          if (lastMessage && lastMessage.role === 'assistant') {
            const updatedMessage: ChatMessage = {
              ...lastMessage,
              content: lastMessage.content + message.content,
            };
            addMessage(conversationId, updatedMessage);
          }
        }
      } else if (message.type === 'done') {
        setStreaming(false);
        setTypingIndicator(false);
      } else if (message.type === 'error') {
        setError('Streaming error occurred.');
        setStreaming(false);
        setTypingIndicator(false);
      }
    },
    [activeConversationId, initialConversationId, messages, addMessage, setStreaming, setTypingIndicator],
  );

  const loadConversations = useCallback(async () => {
    try {
      const data = await chatApi.getConversations();
      // Update store
      data.forEach((conversation) => addConversation(conversation));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load conversations.');
    }
  }, [addConversation]);

  const loadConversation = useCallback(
    async (id: string) => {
      try {
        const conversation = await chatApi.getConversation(id);
        updateConversation(id, conversation);
        addMessages(id, conversation.messages || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load conversation.');
      }
    },
    [updateConversation, addMessages],
  );

  const sendMessage = useCallback(
    async (content: string, conversationId?: string) => {
      if (!content.trim() || content.length > CHAT_CONSTANTS.MAX_MESSAGE_LENGTH) return;

      setIsSending(true);
      setError(null);
      setTypingIndicator(true);

      const targetConversationId = conversationId || activeConversationId;
      const userMessage: ChatMessage = {
        id: `local-${Date.now()}`,
        role: 'user',
        content: content.trim(),
        timestamp: new Date().toISOString(),
      };

      if (targetConversationId) {
        addMessage(targetConversationId, userMessage);
      }

      try {
        const response: ChatResponse = await chatApi.sendMessage({
          message: content.trim(),
          conversation_id: targetConversationId ?? undefined,
        });

        const assistantMessage: ChatMessage = {
          id: response.message_id,
          role: 'assistant',
          content: response.response || response.text || response.message || '',
          intent: response.intent,
          confidence: response.intent_confidence,
          timestamp: response.timestamp,
          conversation_id: response.conversation_id,
          citations: response.citations,
        };

        const finalConversationId = response.conversation_id || targetConversationId;
        if (finalConversationId) {
          addMessage(finalConversationId, assistantMessage);
          setActiveConversation(finalConversationId);
        }

        return response;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to send message.';
        setError(errorMessage);
        throw err;
      } finally {
        setIsSending(false);
        setTypingIndicator(false);
      }
    },
    [activeConversationId, addMessage, setActiveConversation, setTypingIndicator],
  );

  const deleteConversation = useCallback(
    async (id: string) => {
      try {
        await chatApi.deleteConversation(id);
        removeConversation(id);
        clearMessages(id);
        if (activeConversationId === id) {
          setActiveConversation(null);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete conversation.');
        throw err;
      }
    },
    [removeConversation, clearMessages, activeConversationId, setActiveConversation],
  );

  const clearError = useCallback(() => setError(null), []);

  return {
    isLoading,
    messages: activeConversationId ? messages[activeConversationId] || [] : [],
    conversations,
    activeConversationId,
    isSending,
    isStreaming,
    connectionStatus,
    error,
    sendMessage,
    loadConversations,
    loadConversation,
    deleteConversation,
    setActiveConversation,
    clearError,
  };
}