/**
 * HealthConnect AI - WebSocket Client
 * Real-time communication for chat streaming
 */

import { WS_BASE_URL, STORAGE_KEYS } from './constants';

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'reconnecting' | 'error';

export interface WebSocketMessage {
  type: 'chunk' | 'done' | 'error' | 'message' | 'ping' | 'pong';
  content?: string;
  data?: unknown;
}

interface WebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onStatusChange?: (status: WebSocketStatus) => void;
  onError?: (error: Error) => void;
  autoReconnect?: boolean;
  maxReconnectAttempts?: number;
  reconnectDelayMs?: number;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  private pingInterval: ReturnType<typeof setInterval> | null = null;
  private status: WebSocketStatus = 'disconnected';

  constructor(
    private conversationId: string,
    private options: WebSocketOptions = {},
  ) {}

  connect(): void {
    this.setStatus('connecting');

    const token = this.getToken();
    const url = `${WS_BASE_URL}/ws/chat/${this.conversationId}${token ? `?token=${token}` : ''}`;

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this.setStatus('connected');
        this.startPingInterval();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.options.onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (event) => {
        this.setStatus('error');
        this.options.onError?.(new Error('WebSocket connection error'));
      };

      this.ws.onclose = (event) => {
        this.stopPingInterval();
        this.setStatus('disconnected');

        if (
          this.options.autoReconnect !== false &&
          this.reconnectAttempts < (this.options.maxReconnectAttempts ?? 5)
        ) {
          this.scheduleReconnect();
        }
      };
    } catch (error) {
      this.setStatus('error');
      this.options.onError?.(error as Error);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    this.setStatus('reconnecting');

    const delay = (this.options.reconnectDelayMs ?? 1000) * this.reconnectAttempts;

    if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout);
    this.reconnectTimeout = setTimeout(() => this.connect(), delay);
  }

  private startPingInterval(): void {
    this.stopPingInterval();
    this.pingInterval = setInterval(() => {
      this.send({ type: 'ping' });
    }, 30000);
  }

  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  }

  private setStatus(status: WebSocketStatus): void {
    this.status = status;
    this.options.onStatusChange?.(status);
  }

  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent.');
    }
  }

  sendChatMessage(content: string): void {
    this.send({ type: 'message', content });
  }

  disconnect(): void {
    this.stopPingInterval();
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.setStatus('disconnected');
  }

  getStatus(): WebSocketStatus {
    return this.status;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}