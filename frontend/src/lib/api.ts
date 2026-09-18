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