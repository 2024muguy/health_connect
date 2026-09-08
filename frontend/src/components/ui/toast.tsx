'use client';

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { Check, Info, X, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

type ToastVariant = 'success' | 'info' | 'warning' | 'error';

interface Toast {
  id: string;
  message: string;
  variant: ToastVariant;
  duration?: number;
}

interface ToastContextValue {
  toast: (message: string, variant?: ToastVariant, duration?: number) => void;
  dismissToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToastContext() {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToastContext must be used within ToastProvider');
  return context;
}

const variantIcons: Record<ToastVariant, typeof Check> = {
  success: Check,
  info: Info,
  warning: AlertTriangle,
  error: X,
};

const variantStyles: Record<ToastVariant, string> = {
  success: 'text-[hsl(166_40%_36%)] bg-primary/10',
  info: 'text-primary bg-primary/10',
  warning: 'text-[hsl(32_66%_37%)] bg-accent/18',
  error: 'text-destructive bg-destructive/10',
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback(
    (message: string, variant: ToastVariant = 'info', duration = 4000) => {
      const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      setToasts((prev) => [...prev, { id, message, variant, duration }]);

      if (duration > 0) {
        setTimeout(() => dismissToast(id), duration);
      }
    },
    [dismissToast],
  );

  return (
    <ToastContext.Provider value={{ toast, dismissToast }}>
      {children}
      <Toaster toasts={toasts} onDismiss={dismissToast} />
    </ToastContext.Provider>
  );
}

function Toaster({ toasts, onDismiss }: { toasts: Toast[]; onDismiss: (id: string) => void }) {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2">
      {toasts.map((toast) => {
        const Icon = variantIcons[toast.variant];
        return (
          <div
            key={toast.id}
            role="alert"
            className={cn(
              'flex items-center gap-3 min-w-[280px] max-w-[400px] px-4 py-3 rounded-xl border border-border bg-card shadow-xl animate-rise',
            )}
          >
            <div className={cn('w-7 h-7 rounded-lg grid place-items-center', variantStyles[toast.variant])}>
              <Icon size={15} />
            </div>
            <p className="flex-1 text-xs text-foreground font-medium">{toast.message}</p>
            <button
              onClick={() => onDismiss(toast.id)}
              className="text-muted-foreground hover:text-foreground transition-colors"
              aria-label="Dismiss"
            >
              <X size={14} />
            </button>
          </div>
        );
      })}
    </div>
  );
}

// Re-export for compatibility
export { ToastProvider as Toaster };