/**
 * HealthConnect AI - useToast Hook
 * Toast notification management
 */

'use client';

import { useCallback } from 'react';
import { useUIStore } from '@/stores/ui-store';

type ToastVariant = 'success' | 'info' | 'warning' | 'error';

interface UseToastReturn {
  toast: (message: string, variant?: ToastVariant, duration?: number) => void;
  dismissToast: (id: string) => void;
  clearAllToasts: () => void;
}

export function useToast(): UseToastReturn {
  const { addToast, removeToast } = useUIStore();

  const toast = useCallback(
    (message: string, variant: ToastVariant = 'info', duration: number = 4000) => {
      addToast({ message, variant, duration });

      if (duration > 0) {
        const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2)}`;
        setTimeout(() => removeToast(id), duration);
      }
    },
    [addToast, removeToast],
  );

  const dismissToast = useCallback(
    (id: string) => {
      removeToast(id);
    },
    [removeToast],
  );

  const clearAllToasts = useCallback(() => {
    // Clear all toasts by removing each one
    // This would need access to all toast IDs
    // For now, we can trigger a full clear through the store
  }, []);

  return {
    toast,
    dismissToast,
    clearAllToasts,
  };
}