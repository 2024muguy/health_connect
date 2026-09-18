/**
 * HealthConnect AI - Auth Store (Zustand)
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { UserProfile } from '@/types';
import { STORAGE_KEYS } from '@/lib/constants';

interface AuthState {
  user: UserProfile | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  
  setUser: (user: UserProfile | null) => void;
  setTokens: (accessToken: string, refreshToken?: string) => void;
  clearAuth: () => void;
  updateUser: (updates: Partial<UserProfile>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      
      setUser: (user) =>
        set({
          user,
          isAuthenticated: !!user,
        }),
      
      setTokens: (accessToken, refreshToken) =>
        set((state) => {
          // Mirror tokens into raw localStorage keys so `api-client.ts`
          // (which reads STORAGE_KEYS.ACCESS_TOKEN) can find them too.
          if (typeof window !== 'undefined') {
            try {
              localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, accessToken);
              if (refreshToken) {
                localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
              }
            } catch {}
          }
          return {
            accessToken,
            refreshToken: refreshToken ?? state.refreshToken,
            isAuthenticated: !!accessToken,
          };
        }),
      
      clearAuth: () =>
        set(() => {
          // Also clear the raw localStorage keys used by api-client.ts
          if (typeof window !== 'undefined') {
            try {
              localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
              localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
            } catch {}
          }
          return {
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
          };
        }),
      
      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),
    }),
    {
      name: 'healthconnect-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);