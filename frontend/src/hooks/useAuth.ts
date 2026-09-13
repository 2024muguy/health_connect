/**
 * HealthConnect AI - useAuth Hook
 * Authentication state management and operations
 */

'use client';

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/stores/auth-store';
import { getAccessToken, getRefreshToken, clearTokens } from '@/lib/api-client';
import type { LoginRequest, RegisterRequest, RegisterPayload, UserProfile } from '@/types';

interface UseAuthReturn {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  clearError: () => void;
}

function normalizeUser(raw: any): UserProfile {
  const full: string = raw?.full_name || '';
  const parts = full.trim().split(/\s+/);
  const firstName = raw?.firstName || parts[0] || '';
  const lastName = raw?.lastName || parts.slice(1).join(' ') || '';
  const initials =
    (firstName.charAt(0) + lastName.charAt(0)).toUpperCase() ||
    (raw?.email?.[0] || 'U').toUpperCase();

  return {
    user_id: raw?.user_id || raw?.id || '',
    email: raw?.email || '',
    full_name: full,
    roles: Array.isArray(raw?.roles) ? raw.roles : ['user'],
    firstName,
    lastName,
    phone: raw?.phone,
    initials,
    createdAt: raw?.created_at || raw?.createdAt,
    updatedAt: raw?.updated_at || raw?.updatedAt,
  };
}

export function useAuth(): UseAuthReturn {
  const router = useRouter();
  const { user, isAuthenticated, setUser, setTokens, clearAuth } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      const accessToken = getAccessToken();
      const refreshToken = getRefreshToken();

      if (!accessToken && !refreshToken) {
        clearAuth();
        setIsLoading(false);
        return;
      }

      try {
        // Try to get user profile
        const profile = await authApi.me(accessToken ?? undefined);
        setUser(normalizeUser(profile));
      } catch {
        // Token might be expired, try refresh
        if (refreshToken) {
          try {
            const response = await authApi.refresh(refreshToken);
            setTokens(response.access_token, response.refresh_token);
            const profile = await authApi.me(response.access_token);
            setUser(normalizeUser(profile));
          } catch {
            clearAuth();
          }
        } else {
          clearAuth();
        }
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [setUser, setTokens, clearAuth]);

  const login = useCallback(
    async (data: LoginRequest) => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await authApi.login(data);
        setTokens(response.access_token, response.refresh_token);

        // Pass the token explicitly — don't rely on the interceptor
        const profile = await authApi.me(response.access_token);
        setUser(normalizeUser(profile));

        router.push('/dashboard');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Login failed. Please try again.');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [router, setTokens, setUser],
  );

  const register = useCallback(
    async (data: RegisterRequest) => {
      setIsLoading(true);
      setError(null);

      try {
        // Merge firstName + lastName into full_name for backend
        const payload: RegisterPayload = {
          email: data.email,
          password: data.password,
          full_name:
            [data.firstName, data.lastName].filter(Boolean).join(' ').trim() ||
            data.email.split('@')[0],
          phone: data.phone,
        };

        const response = await authApi.register(payload);
        setTokens(response.access_token, response.refresh_token);

        const profile = await authApi.me(response.access_token);
        setUser(normalizeUser(profile));

        router.push('/dashboard');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Registration failed. Please try again.');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [router, setTokens, setUser],
  );

  const logout = useCallback(async () => {
    setIsLoading(true);

    try {
      await authApi.logout();
    } catch {
      // Ignore logout API errors
    } finally {
      clearAuth();
      clearTokens();
      setIsLoading(false);
      router.push('/login');
    }
  }, [router, clearAuth]);

  const refreshProfile = useCallback(async () => {
    try {
      const token = getAccessToken();
      const profile = await authApi.me(token ?? undefined);
      setUser(normalizeUser(profile));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh profile.');
    }
  }, [setUser]);

  const clearError = useCallback(() => setError(null), []);

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    refreshProfile,
    clearError,
  };
}