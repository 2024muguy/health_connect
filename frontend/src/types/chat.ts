/**
 * HealthConnect AI - Chat Types
 * Extended for Week 7: streaming, memory, uncertainty, booking.
 */

export type ChatRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
  /** Alias for createdAt — some legacy components read `timestamp` */
  timestamp?: string;
  // Week 7 additions
  isStreaming?: boolean;
  intent?: string;
  safetyCategory?: string;
  requiresHuman?: boolean;
  citations?: ChatCitation[];
  confidence?: number | null;
  retrievalScore?: number | null;
  judgeScore?: number | null;
  uncertaintyGated?: boolean;
  bookingCompleted?: boolean;
}

export interface ChatCitation {
  index?: string;
  chunk_id?: string;
  document_id?: string;
  section?: string | null;
  title?: string;
  formatted?: string;
}

export interface ChatResponse {
  message_id?: string;
  conversation_id?: string;
  response: string;
  text?: string;
  message?: string;
  intent: string;
  intent_confidence?: number;
  safety_category: string;
  safety_score?: number;
  requires_human?: boolean;
  citations?: ChatCitation[];
  action_performed?: string | null;
  processing_time_ms?: number;
  // Week 7 additions
  confidence?: number | null;
  retrieval_score?: number | null;
  judge_score?: number | null;
  uncertainty_gated?: boolean;
  booking_completed?: boolean;
  timestamp?: string;
}

export interface Conversation {
  id: string;
  conversation_code: string;
  session_token: string;
  status: string;
  started_at?: string;
  last_activity_at?: string;
  summary?: string | null;
  message_count?: number;
  // UI helpers (optional; can be derived from backend fields)
  title?: string;
  preview?: string;
  updatedAt?: string;
  createdAt?: string;
}

// Streaming frame types (SSE and WS both emit these)
export interface StreamFrame {
  type: 'start' | 'chunk' | 'done' | 'error' | 'ack' | 'message' | 'ping' | 'pong';
  text?: string;
  error?: string;
  conversation_id?: string;
  intent?: string;
  safety_category?: string;
  citations?: ChatCitation[];
  requires_human?: boolean;
}


export interface ChatRequest {
  message: string;
  conversation_id?: string;
  session_token?: string;
}
