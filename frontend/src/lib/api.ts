/**
 * HealthConnect AI - API Helper Functions
 * Typed API calls for all endpoints
 */

import { apiClient } from './api-client';
import { API_ENDPOINTS } from './constants';
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterPayload,
  ChatRequest,
  ChatResponse,
  Conversation,
  Appointment,
  AppointmentCreate,
  ClinicInfo,
  EscalationCreate,
  AnalyticsMetrics,
  UserProfile,
} from '@/types';

// ============================================
// Auth API
// ============================================
export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<LoginResponse>(API_ENDPOINTS.AUTH.LOGIN, data),

  register: (data: RegisterPayload) =>
    apiClient.post<LoginResponse>(API_ENDPOINTS.AUTH.REGISTER, data),

  refresh: (refreshToken: string) =>
    apiClient.post<LoginResponse>(API_ENDPOINTS.AUTH.REFRESH, { refresh_token: refreshToken }),

  logout: () =>
    apiClient.post(API_ENDPOINTS.AUTH.LOGOUT),

  me: (accessToken?: string) =>
    apiClient.get<UserProfile>(
      API_ENDPOINTS.AUTH.ME,
      accessToken
        ? { headers: { Authorization: `Bearer ${accessToken}` } }
        : undefined,
    ),
};

// ============================================
// Chat API
// ============================================
export const chatApi = {
  /**
   * Stream a chat response token-by-token via SSE.
   * Returns an async iterator of frames.
   */
  sendMessageStream: async function* (payload: {
    message: string;
    conversation_id?: string;
    session_token?: string;
  }): AsyncGenerator<{ type: string; text?: string; [key: string]: unknown }> {
    const { getAccessToken } = await import('@/lib/api-client');
    const token = getAccessToken();

    const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    console.log('[SSE] fetch →', `${API_BASE}/chat/message/stream`);
    const res = await fetch(`${API_BASE}/chat/message/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok || !res.body) {
      yield { type: 'error', error: `HTTP ${res.status}` };
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    console.log('[SSE] reader acquired, starting read loop');

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        console.log('[SSE] reader done, buffer remainder:', buffer.length);
        break;
      }
      const decoded = decoder.decode(value, { stream: true });
      console.log('[SSE] raw chunk:', JSON.stringify(decoded.slice(0, 80)));
      buffer += decoded;

      const frames = buffer.split('\n\n');
      buffer = frames.pop() ?? '';
      console.log('[SSE] frames parsed:', frames.length);

      for (const frame of frames) {
        const line = frame.split('\n').find((l) => l.startsWith('data: '));
        if (!line) {
          console.log('[SSE] no data line in frame:', JSON.stringify(frame.slice(0, 60)));
          continue;
        }
        try {
          const json = JSON.parse(line.slice(6));
          console.log('[SSE] yielding frame type:', json.type);
          yield json;
        } catch (e) {
          console.log('[SSE] parse error:', e);
        }
      }
    }
  },

  sendMessage: (data: ChatRequest) =>
    apiClient.post<ChatResponse>(API_ENDPOINTS.CHAT.MESSAGE, data),

  getConversations: () =>
    apiClient.get<Conversation[]>(API_ENDPOINTS.CHAT.CONVERSATIONS),

  getConversation: (id: string) =>
    apiClient.get<Conversation>(API_ENDPOINTS.CHAT.CONVERSATION(id)),

  deleteConversation: (id: string) =>
    apiClient.delete(API_ENDPOINTS.CHAT.CONVERSATION(id)),

  submitFeedback: (data: { conversationId: string; satisfactionScore: number }) =>
    apiClient.post(API_ENDPOINTS.CHAT.FEEDBACK, data),
};

// ============================================
// Appointments API
// ============================================
export const appointmentApi = {
  list: (params?: { status?: string }) =>
    apiClient.get<any>(API_ENDPOINTS.APPOINTMENTS.LIST, { params }),

  create: (data: AppointmentCreate) =>
    apiClient.post<Appointment>(API_ENDPOINTS.APPOINTMENTS.CREATE, data),

  get: (id: string) =>
    apiClient.get<Appointment>(API_ENDPOINTS.APPOINTMENTS.DETAIL(id)),

  update: (id: string, data: Partial<AppointmentCreate>) =>
    apiClient.put<Appointment>(API_ENDPOINTS.APPOINTMENTS.UPDATE(id), data),

  reschedule: (id: string, newDatetime: string) =>
    apiClient.post(API_ENDPOINTS.APPOINTMENTS.RESCHEDULE(id), { new_datetime: newDatetime }),

  cancel: (id: string, reason?: string) =>
    apiClient.post(API_ENDPOINTS.APPOINTMENTS.CANCEL(id), { reason, confirm_cancellation: true }),

  getAvailability: (params: { date: string; service?: string }) =>
    apiClient.get<any>(API_ENDPOINTS.APPOINTMENTS.AVAILABILITY, { params }),
};

// ============================================
// Clinic API
// ============================================
export const clinicApi = {
  getInfo: () =>
    apiClient.get<ClinicInfo>(API_ENDPOINTS.CLINIC.INFO),

  getLocations: () =>
    apiClient.get(API_ENDPOINTS.CLINIC.LOCATIONS),

  getServices: () =>
    apiClient.get(API_ENDPOINTS.CLINIC.SERVICES),

  getHours: (locationId?: string) =>
    apiClient.get(API_ENDPOINTS.CLINIC.HOURS, { params: { location_id: locationId } }),
};

// ============================================
// Escalations API
// ============================================
export const escalationApi = {
  create: (data: EscalationCreate) =>
    apiClient.post(API_ENDPOINTS.ESCALATIONS.CREATE, data),

  list: (params?: { status?: string }) =>
    apiClient.get(API_ENDPOINTS.ESCALATIONS.LIST, { params }),

  get: (code: string) =>
    apiClient.get(API_ENDPOINTS.ESCALATIONS.DETAIL(code)),
};

// ============================================
// Analytics API (Admin)
// ============================================
export const analyticsApi = {
  getMetrics: () =>
    apiClient.get<AnalyticsMetrics>(API_ENDPOINTS.ANALYTICS.METRICS),

  getReport: (period: string = 'daily') =>
    apiClient.get(API_ENDPOINTS.ANALYTICS.REPORT, { params: { period } }),

  trackEvent: (eventType: string, eventData?: Record<string, unknown>) =>
    apiClient.post(API_ENDPOINTS.ANALYTICS.EVENTS, { event_type: eventType, event_data: eventData }),
};