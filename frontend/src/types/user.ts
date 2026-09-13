/**
 * HealthConnect AI - User Types
 */

// ============================================
// User Profile (what backend /me returns)
// ============================================
export interface UserProfile {
  user_id: string;
  email: string;
  full_name: string;
  roles: string[];
  // Optional client-side enrichments (derived on the frontend)
  firstName?: string;
  lastName?: string;
  phone?: string;
  initials?: string;
  createdAt?: string;
  updatedAt?: string;
}

// ============================================
// Auth requests
// ============================================
export interface LoginRequest {
  email: string;
  password: string;
}

/** What the register form collects (UI-facing) */
export interface RegisterRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phone?: string;
}

/** What the API actually sends to the backend */
export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
}

// ============================================
// Auth responses
// ============================================
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthState {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
