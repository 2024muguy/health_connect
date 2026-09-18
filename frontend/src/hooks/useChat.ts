/**
 * HealthConnect AI - useChat Hook
 * Supports:
 *   - Token-by-token streaming via SSE (/message/stream)
 *   - WebSocket streaming (chunk frames)
 *   - Non-streaming fallback
 *   - Memory + uncertainty metadata
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
  sendMessageStreaming: (content: string, conversationId?: string) => Promise<void>;
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

  // -------- WebSocket lifecycle --------
  useEffect(() => {
    // Week 7: WS disabled. SSE (/message/stream) is the streaming path.
    // To re-enable later, flip `WS_ENABLED` below to true.
    const WS_ENABLED = false;
    if (!WS_ENABLED) {
      return;
    }
    if (!initialConversationId && !activeConversationId) return;
    const conversationId = initialConversationId || activeConversationId;
    if (!conversationId) return;

    const ws = WebSocketClient.getInstance(conversationId, {
      onMessage: handleWebSocketMessage,
      onStatusChange: setConnectionStatus,
      onError: (err) => setError(err.message),
    });

    if (typeof window !== 'undefined') {
      // Refresh token before connecting: /auth/me triggers the interceptor
      // which auto-refreshes on 401. Then read the fresh token from storage.
      (async () => {
        try {
          const { apiClient } = await import('@/lib/api-client');
          await apiClient.get('/auth/me');
        } catch {
          // ignore — we'll still try to connect with whatever we have
        } finally {
          const fresh = window.localStorage.getItem('hc_access_token');
          if (fresh) ws.setToken(fresh);
          ws.connect();
        }
      })();
    } else {
      ws.connect();
    }
    wsRef.current = ws;

    return () => {
      ws.disconnect();
      wsRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialConversationId, activeConversationId]);

  const handleWebSocketMessage = useCallback(
    (message: WebSocketMessage) => {
      const conversationId = activeConversationId || initialConversationId;
      if (!conversationId) return;

      const currentMessages = messages[conversationId] || [];
      const lastMessage = currentMessages[currentMessages.length - 1];

      if (message.type === 'chunk' && message.text) {
        setStreaming(true);
        if (lastMessage && lastMessage.role === 'assistant') {
          addMessage(conversationId, {
            ...lastMessage,
            content: lastMessage.content + message.text,
            isStreaming: true,
          });
        }
      } else if (message.type === 'done') {
        setStreaming(false);
        setTypingIndicator(false);
        if (lastMessage && lastMessage.role === 'assistant') {
          addMessage(conversationId, { ...lastMessage, isStreaming: false });
        }
      } else if (message.type === 'error') {
        setError(message.error || 'Streaming error');
        setStreaming(false);
        setTypingIndicator(false);
      }
    },
    [activeConversationId, initialConversationId, messages, addMessage, setStreaming, setTypingIndicator],
  );

  // -------- Non-streaming send --------
  const sendMessage = useCallback(
    async (content: string, conversationId?: string): Promise<ChatResponse | undefined> => {
      const convId = conversationId || activeConversationId || initialConversationId;
      setIsSending(true);
      setError(null);

      try {
        const userMessage: ChatMessage = {
          id: `u-${Date.now()}`,
          role: 'user',
          content,
          createdAt: new Date().toISOString(),
        };
        if (convId) addMessage(convId, userMessage);
        setTypingIndicator(true);

        const response = await chatApi.sendMessage({
          message: content,
          conversation_id: convId,
        } as any);

        const responseText = response.response || response.text || response.message || '';

        if (convId) {
          addMessage(convId, {
            id: response.message_id || `a-${Date.now()}`,
            role: 'assistant',
            content: responseText,
            createdAt: new Date().toISOString(),
            intent: response.intent,
            safetyCategory: response.safety_category,
            requiresHuman: response.requires_human,
            citations: response.citations,
            confidence: response.confidence ?? null,
            retrievalScore: response.retrieval_score ?? null,
            judgeScore: response.judge_score ?? null,
            uncertaintyGated: response.uncertainty_gated,
            bookingCompleted: response.booking_completed,
          });
        }
        return response;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Send failed');
        return undefined;
      } finally {
        setIsSending(false);
        setTypingIndicator(false);
      }
    },
    [activeConversationId, initialConversationId, addMessage, setTypingIndicator],
  );

  // -------- SSE streaming send --------
  const sendMessageStreaming = useCallback(
    async (content: string, conversationId?: string): Promise<void> => {
      const convId = conversationId || activeConversationId || initialConversationId;
      setIsSending(true);
      setStreaming(true);
      setError(null);

      try {
        console.log('[useChat] sendMessageStreaming called for:', content);
        // Add user message
        const userMessage: ChatMessage = {
          id: `u-${Date.now()}`,
          role: 'user',
          content,
          createdAt: new Date().toISOString(),
        };
        if (convId) addMessage(convId, userMessage);

        // Placeholder assistant message to receive chunks
        const assistantPlaceholder: ChatMessage = {
          id: `a-${Date.now()}`,
          role: 'assistant',
          content: '',
          createdAt: new Date().toISOString(),
          isStreaming: true,
        };
        if (convId) addMessage(convId, assistantPlaceholder);
        setTypingIndicator(true);

        const sessionToken =
          (typeof window !== 'undefined' && window.localStorage.getItem('hc_session_token')) ||
          undefined;

        let accumulated = '';
        let doneMeta: Record<string, unknown> = {};

        console.log('[useChat] invoking chatApi.sendMessageStream, typeof:',
          typeof (chatApi as any).sendMessageStream);

        let frameCount = 0;
        for await (const frame of (chatApi as any).sendMessageStream({
          message: content,
          conversation_id: convId,
          session_token: sessionToken,
        })) {
          frameCount++;
          console.log('[useChat] frame', frameCount, 'type:', frame.type);
          if (frame.type === 'chunk' && frame.text) {
            accumulated += frame.text;
            // Replace the last assistant message content
            const list = (useChatStore.getState().messages[convId || ''] || []);
            const lastIdx = list.length - 1;
            if (lastIdx >= 0 && list[lastIdx].role === 'assistant') {
              const updated: ChatMessage = {
                ...list[lastIdx],
                content: accumulated,
                isStreaming: true,
              };
              addMessage(convId || '', updated);
            }
          } else if (frame.type === 'done') {
            doneMeta = frame;
            setStreaming(false);
            setTypingIndicator(false);
            const list = (useChatStore.getState().messages[convId || ''] || []);
            const lastIdx = list.length - 1;
            if (lastIdx >= 0 && list[lastIdx].role === 'assistant') {
              const updated: ChatMessage = {
                ...list[lastIdx],
                content: frame.text || accumulated,
                isStreaming: false,
                intent: frame.intent,
                safetyCategory: frame.safety_category,
                requiresHuman: frame.requires_human,
                citations: frame.citations,
              };
              addMessage(convId || '', updated);
            }
          } else if (frame.type === 'error') {
            setError(frame.error || 'Stream error');
            setStreaming(false);
            setTypingIndicator(false);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Stream failed');
        setStreaming(false);
        setTypingIndicator(false);
      } finally {
        setIsSending(false);
      }
    },
    [activeConversationId, initialConversationId, addMessage, setStreaming, setTypingIndicator],
  );

  // -------- Misc --------
  const loadConversations = useCallback(async () => {
    try {
      const data = await chatApi.getConversations();
      (data as unknown as Conversation[]).forEach(addConversation);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load conversations');
    }
  }, [addConversation]);

  const loadConversation = useCallback(
    async (id: string) => {
      setIsLoading(true);
      try {
        const data = await chatApi.getConversation(id);
        const msgs = (data as any).messages || [];
        if (msgs.length) {
          addMessages(
            id,
            msgs.map((m: any) => ({
              id: m.id || `m-${Math.random()}`,
              role: m.role,
              content: m.content,
              createdAt: m.timestamp || new Date().toISOString(),
            })),
          );
        }
        setActiveConversation(id);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load conversation');
      } finally {
        setIsLoading(false);
      }
    },
    [addMessages, setActiveConversation],
  );

  const deleteConversation = useCallback(
    async (id: string) => {
      try {
        await chatApi.deleteConversation(id);
        removeConversation(id);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete conversation');
      }
    },
    [removeConversation],
  );

  const clearError = useCallback(() => setError(null), []);

  // Ensure session token exists
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!window.localStorage.getItem('hc_session_token')) {
      const token = `sess-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
      window.localStorage.setItem('hc_session_token', token);
    }
  }, []);

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
    sendMessageStreaming,
    loadConversations,
    loadConversation,
    deleteConversation,
    setActiveConversation,
    clearError,
  };
}
