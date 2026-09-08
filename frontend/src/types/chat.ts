/**
 * HealthConnect AI - Chat Types
 */

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  intent?: string;
  confidence?: number;
  timestamp: string;
  conversation_id?: string;
  citations?: Citation[];
}

export interface Citation {
  index: string;
  chunk_id: string;
  document_id: string;
  section?: string;
  formatted: string;
}

export interface Conversation {
  id: string;
  conversation_code: string;
  title: string;
  preview: string;
  status: 'active' | 'completed' | 'escalated' | 'timeout';
  started_at: string;
  updatedAt: string;
  ended_at?: string;
  messageCount: number;
  messages: ChatMessage[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  session_token?: string;
}

export interface ChatResponse {
  message_id: string;
  conversation_id: string;
  message: string;
  intent: string;
  intent_confidence: number;
  safety_category: string;
  requires_human: boolean;
  citations: Citation[];
  timestamp: string;
}