/**
 * HealthConnect AI - Application Constants
 */

// API Configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
export const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

// App Information
export const APP_NAME = 'HealthConnect AI';
export const APP_VERSION = '1.0.0';
export const APP_DESCRIPTION = 'Your care, thoughtfully organized.';

// Storage Keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'hc_access_token',
  REFRESH_TOKEN: 'hc_refresh_token',
  USER_PROFILE: 'hc_user_profile',
  THEME: 'hc_theme',
  CHAT_HISTORY: 'hc_chat_history',
} as const;

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',
  },
  CHAT: {
    MESSAGE: '/chat/message',
    STREAM: '/chat/stream',
    CONVERSATIONS: '/chat/conversations',
    CONVERSATION: (id: string) => `/chat/conversations/${id}`,
    FEEDBACK: '/chat/feedback',
  },
  APPOINTMENTS: {
    LIST: '/appointments',
    CREATE: '/appointments',
    DETAIL: (id: string) => `/appointments/${id}`,
    UPDATE: (id: string) => `/appointments/${id}`,
    RESCHEDULE: (id: string) => `/appointments/${id}/reschedule`,
    CANCEL: (id: string) => `/appointments/${id}/cancel`,
    AVAILABILITY: '/appointments/availability',
  },
  CLINIC: {
    INFO: '/clinic/info',
    LOCATIONS: '/clinic/locations',
    SERVICES: '/clinic/services',
    HOURS: '/clinic/hours',
    INSURANCE: '/clinic/insurance',
  },
  ESCALATIONS: {
    CREATE: '/escalations',
    LIST: '/escalations',
    DETAIL: (code: string) => `/escalations/${code}`,
    ASSIGN: (code: string) => `/escalations/${code}/assign`,
    RESOLVE: (code: string) => `/escalations/${code}/resolve`,
  },
  ADMIN: {
    STATS: '/admin/stats',
    SYSTEM: '/admin/system',
    USERS: '/admin/users',
    AUDIT: '/admin/audit',
  },
  ANALYTICS: {
    METRICS: '/analytics/metrics',
    REPORT: '/analytics/report',
    EVENTS: '/analytics/events',
  },
} as const;

// Toast Messages
export const TOAST_MESSAGES = {
  LOGIN_SUCCESS: 'Welcome back!',
  LOGIN_ERROR: 'Invalid email or password.',
  LOGOUT_SUCCESS: 'You have been logged out.',
  REGISTER_SUCCESS: 'Account created successfully!',
  PROFILE_UPDATED: 'Profile updated successfully.',
  APPOINTMENT_BOOKED: 'Appointment booked successfully!',
  APPOINTMENT_CANCELLED: 'Appointment cancelled.',
  APPOINTMENT_RESCHEDULED: 'Appointment rescheduled.',
  MESSAGE_SENT: 'Message sent.',
  MESSAGE_ERROR: 'Failed to send message. Please try again.',
  CONVERSATION_DELETED: 'Conversation deleted.',
  FEEDBACK_SUBMITTED: 'Thank you for your feedback!',
  ESCALATION_CREATED: 'Your request has been escalated.',
  NETWORK_ERROR: 'Network error. Please check your connection.',
} as const;

// Time Constants
export const TIME_CONSTANTS = {
  SESSION_TIMEOUT_MINUTES: 30,
  TOKEN_REFRESH_INTERVAL_MS: 5 * 60 * 1000, // 5 minutes
  DEBOUNCE_DELAY_MS: 300,
  TYPING_INDICATOR_DELAY_MS: 1000,
} as const;

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
} as const;

// Chat Constants
export const CHAT_CONSTANTS = {
  MAX_MESSAGE_LENGTH: 2000,
  QUICK_REPLIES: [
    'Book an appointment',
    'Check clinic hours',
    'Cancel appointment',
    'Talk to a human',
  ],
  SUGGESTIONS: [
    'How should I prepare for my next visit?',
    'Which services are available at the clinic?',
    'What should I bring to my appointment?',
    'How do I reschedule?',
  ],
} as const;

// Safety Categories
export const SAFETY_CATEGORIES = {
  SAFE: 'safe',
  MEDICAL_ADVICE: 'medical_advice_request',
  EMERGENCY: 'emergency',
  PRESCRIPTION: 'prescription_request',
  TEST_RESULT: 'test_result_query',
  OUT_OF_SCOPE: 'out_of_scope',
  PII_REQUEST: 'pii_request',
  ABUSIVE: 'abusive_language',
} as const;

// Appointment Types
export const APPOINTMENT_TYPES = [
  'General Consultation',
  'Follow-up Visit',
  'Specialist Consultation',
  'Laboratory Services',
  'Imaging Services',
  'Vaccination',
  'Physical Examination',
  'Telehealth',
] as const;

// Appointment Status
export const APPOINTMENT_STATUS = {
  SCHEDULED: 'scheduled',
  CONFIRMED: 'confirmed',
  CHECKED_IN: 'checked_in',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled',
  NO_SHOW: 'no_show',
  RESCHEDULED: 'rescheduled',
  PENDING: 'pending',
} as const;