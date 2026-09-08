/**
 * HealthConnect AI - useWebSocket Hook
 * Generic WebSocket connection hook
 */

'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketClient, type WebSocketStatus, type WebSocketMessage } from '@/lib/websocket';

interface UseWebSocketReturn {
  status: WebSocketStatus;
  isConnected: boolean;
  send: (message: WebSocketMessage) => void;
  lastMessage: WebSocketMessage | null;
  reconnect: () => void;
}

export function useWebSocket(
  conversationId: string | null,
  options: {
    onMessage?: (message: WebSocketMessage) => void;
    onStatusChange?: (status: WebSocketStatus) => void;
    autoReconnect?: boolean;
  } = {},
): UseWebSocketReturn {
  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocketClient | null>(null);

  const handleMessage = useCallback(
    (message: WebSocketMessage) => {
      setLastMessage(message);
      options.onMessage?.(message);
    },
    [options.onMessage],
  );

  const handleStatusChange = useCallback(
    (newStatus: WebSocketStatus) => {
      setStatus(newStatus);
      options.onStatusChange?.(newStatus);
    },
    [options.onStatusChange],
  );

  const connect = useCallback(() => {
    if (!conversationId) return;

    if (wsRef.current) {
      wsRef.current.disconnect();
    }

    const ws = new WebSocketClient(conversationId, {
      onMessage: handleMessage,
      onStatusChange: handleStatusChange,
      autoReconnect: options.autoReconnect ?? true,
    });

    ws.connect();
    wsRef.current = ws;
  }, [conversationId, handleMessage, handleStatusChange, options.autoReconnect]);

  useEffect(() => {
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.disconnect();
        wsRef.current = null;
      }
    };
  }, [connect]);

  const send = useCallback((message: WebSocketMessage) => {
    wsRef.current?.send(message);
  }, []);

  return {
    status,
    isConnected: status === 'connected',
    send,
    lastMessage,
    reconnect: connect,
  };
}