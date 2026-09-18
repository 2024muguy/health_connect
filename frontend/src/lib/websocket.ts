/**
 * HealthConnect AI - WebSocket Client (Production-Ready)
 * ======================================================
 * - Singleton per conversation (no duplicate connections)
 * - Exponential backoff reconnection
 * - Single keepalive ping every 30s
 * - Handles React Strict Mode double-mount
 */

export type WebSocketStatus =
  | 'connecting'
  | 'connected'
  | 'disconnected'
  | 'reconnecting'
  | 'error';

export interface WebSocketMessage {
  type: 'message' | 'ping' | 'pong' | 'error' | 'ack';
  message?: string;
  response?: string;
  message_id?: string;
  conversation_id?: string;
  intent?: string;
  safety_category?: string;
  citations?: any[];
  error?: string;
  timestamp?: string;
}

interface WebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onStatusChange?: (status: WebSocketStatus) => void;
  onError?: (error: Error) => void;
  // Optional tuning — ignored for now but kept for API compatibility
  autoReconnect?: boolean;
  maxReconnectAttempts?: number;
  reconnectDelayMs?: number;
}

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
const PING_INTERVAL_MS = 30_000;
const RECONNECT_BASE_MS = 1_000;
const RECONNECT_MAX_MS = 30_000;
const MAX_RECONNECT_ATTEMPTS = 10;

export class WebSocketClient {
  private static instances = new Map<string, WebSocketClient>();

  private ws: WebSocket | null = null;
  private conversationId: string;
  private token: string | null = null;
  private options: WebSocketOptions = {};
  private status: WebSocketStatus = 'disconnected';
  private reconnectAttempts = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private pingTimer: ReturnType<typeof setInterval> | null = null;
  private intentionallyClosed = false;

  static getInstance(
    conversationId: string,
    options: WebSocketOptions = {},
  ): WebSocketClient {
    const existing = WebSocketClient.instances.get(conversationId);
    if (existing) {
      existing.options = { ...existing.options, ...options };
      return existing;
    }
    const client = new WebSocketClient(conversationId, options);
    WebSocketClient.instances.set(conversationId, client);
    return client;
  }

  static destroy(conversationId: string): void {
    const client = WebSocketClient.instances.get(conversationId);
    if (client) {
      client.close();
      WebSocketClient.instances.delete(conversationId);
    }
  }

  private constructor(conversationId: string, options: WebSocketOptions = {}) {
    this.conversationId = conversationId;
    this.options = options;
  }

  setToken(token: string | null): void {
    this.token = token;
  }

  private setStatus(status: WebSocketStatus): void {
    if (this.status === status) return;
    this.status = status;
    this.options.onStatusChange?.(status);
  }

  private buildUrl(): string {
    const base = WS_BASE_URL.replace(/\/$/, '');
    const tokenParam = this.token ? `?token=${encodeURIComponent(this.token)}` : '';
    return `${base}/api/v1/ws/chat/${this.conversationId}${tokenParam}`;
  }

  connect(): void {
    if (
      this.ws &&
      (this.ws.readyState === WebSocket.CONNECTING ||
        this.ws.readyState === WebSocket.OPEN)
    ) {
      return;
    }

    // Auto-refresh token from localStorage on every connect attempt
    if (typeof window !== 'undefined') {
      const fresh = window.localStorage.getItem('hc_access_token');
      if (fresh) this.token = fresh;
    }

    this.intentionallyClosed = false;
    this.setStatus('connecting');

    try {
      const url = this.buildUrl();
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('[WS] connected to', this.conversationId);
        this.reconnectAttempts = 0;
        this.setStatus('connected');
        this.startPing();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          if (message.type === 'pong') return;
          this.options.onMessage?.(message);
        } catch (err) {
          console.error('[WS] parse failed:', event.data);
        }
      };

      this.ws.onerror = (event) => {
        console.error('[WS] error:', event);
        this.setStatus('error');
        this.options.onError?.(new Error('WebSocket error'));
      };

      this.ws.onclose = () => {
        this.stopPing();
        this.ws = null;

        if (this.intentionallyClosed) {
          this.setStatus('disconnected');
          return;
        }

        if (this.reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          this.setStatus('reconnecting');
          this.scheduleReconnect();
        } else {
          this.setStatus('error');
        }
      };
    } catch (err) {
      console.error('[WS] connect failed:', err);
      this.setStatus('error');
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) return;
    const delay = Math.min(
      RECONNECT_BASE_MS * Math.pow(2, this.reconnectAttempts),
      RECONNECT_MAX_MS,
    );
    this.reconnectAttempts += 1;
    console.log(`[WS] reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, delay);
  }

  private startPing(): void {
    this.stopPing();
    this.pingTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        try {
          this.ws.send(JSON.stringify({ type: 'ping' }));
        } catch (err) {
          console.warn('[WS] ping failed:', err);
        }
      }
    }, PING_INTERVAL_MS);
  }

  private stopPing(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  send(message: WebSocketMessage): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message));
        return true;
      } catch (err) {
        console.warn('[WS] send failed:', err);
        return false;
      }
    }
    console.warn('[WS] not connected, message not sent');
    return false;
  }

  close(): void {
    this.intentionallyClosed = true;
    this.stopPing();
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      try {
        this.ws.close(1000, 'Client closing');
      } catch {}
      this.ws = null;
    }
    this.setStatus('disconnected');
  }

  disconnect(): void {
    this.close();
  }

  getStatus(): WebSocketStatus {
    return this.status;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
