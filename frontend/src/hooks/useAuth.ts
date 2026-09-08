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
import type { LoginRequest, RegisterRequest, UserProfile } from '@/types';

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
        const profile = await authApi.me();
        setUser(profile);
      } catch {
        // Token might be expired, try refresh
        if (refreshToken) {
          try {
            const response = await authApi.refresh(refreshToken);
            setTokens(response.access_token, response.refresh_token);
            const profile = await authApi.me();
            setUser(profile);
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

        const profile = await authApi.me();
        setUser(profile);

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
        const response = await authApi.register(data);
        setTokens(response.access_token, response.refresh_token);

        const profile = await authApi.me();
        setUser(profile);

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
      const profile = await authApi.me();
      setUser(profile);
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