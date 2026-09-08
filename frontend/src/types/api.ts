/**
 * HealthConnect AI - API Types
 */

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ClinicInfo {
  id: string;
  name: string;
  tagline?: string;
  description?: string;
  address: string;
  phone: string;
  email: string;
  hours: string;
}

export interface ClinicService {
  id: string;
  name: string;
  description: string;
  duration: number;
  category?: string;
}

export interface EscalationCreate {
  conversation_id?: string;
  escalation_type: string;
  tier: number;
  reason: string;
  priority?: 'low' | 'normal' | 'high' | 'critical';
  department?: string;
}

export interface AnalyticsMetrics {
  total_conversations: number;
  total_messages: number;
  total_appointments: number;
  total_escalations: number;
  no_show_rate: number;
  average_response_time_ms: number;
  top_intents: Record<string, number>;
  hourly_activity: Record<string, number>;
}