'use client';
import { useEffect, useRef, useState } from 'react';
import { WebSocketClient, type WebSocketMessage, type WebSocketStatus } from '@/lib/websocket';

interface UseWebSocketOptions {
  conversationId: string | null;
  token: string | null;
  onMessage?: (message: WebSocketMessage) => void;
  enabled?: boolean;
}

export function useWebSocket({ conversationId, token, onMessage, enabled = true }: UseWebSocketOptions) {
  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    if (!enabled || !conversationId || !token) return;
    const client = WebSocketClient.getInstance(conversationId, {
      onMessage: (msg) => onMessageRef.current?.(msg),
      onStatusChange: setStatus,
    });
    client.setToken(token);
    client.connect();
    return () => WebSocketClient.destroy(conversationId);
  }, [conversationId, token, enabled]);

  const send = (message: WebSocketMessage) => {
    if (!conversationId) return false;
    return WebSocketClient.getInstance(conversationId).send(message);
  };

  return { status, send };
}
