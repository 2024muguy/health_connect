'use client';

import { useState, useRef, useEffect } from 'react';
import { Bell, Check, X } from 'lucide-react';
import { useNotifications } from '@/hooks/useNotifications';
import { cn } from '@/lib/utils';

export function NotificationBell() {
  const { notifications, unread, markRead, markAllRead } = useNotifications();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const typeIcon = (type: string) => {
    switch (type) {
      case 'emergency': return '🚨';
      case 'appointment': return '📅';
      case 'promo': return '🎁';
      case 'welcome': return '👋';
      default: return 'ℹ️';
    }
  };

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="relative p-2 rounded-full hover:bg-muted transition-colors"
        aria-label="Notifications"
        data-testid="button-notifications"
      >
        <Bell size={18} />
        {unread > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-destructive text-destructive-foreground text-[9px] font-bold flex items-center justify-center">
            {unread > 9 ? '9+' : unread}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 bg-card border border-border rounded-xl shadow-lg z-50 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-border">
            <strong className="text-sm">Notifications</strong>
            <div className="flex items-center gap-2">
              {unread > 0 && (
                <button
                  onClick={markAllRead}
                  className="text-xs text-primary hover:underline"
                  title="Mark all as read"
                >
                  <Check size={14} className="inline" /> All read
                </button>
              )}
              <button onClick={() => setOpen(false)} className="text-muted-foreground hover:text-foreground">
                <X size={14} />
              </button>
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-6 text-center text-xs text-muted-foreground">
                No notifications yet
              </div>
            ) : (
              notifications.map((n) => (
                <button
                  key={n.id}
                  onClick={() => markRead(n.id)}
                  className={cn(
                    'w-full text-left px-4 py-3 border-b border-border/50 hover:bg-muted/50 transition-colors',
                    !n.read && 'bg-primary/5'
                  )}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-lg">{typeIcon(n.type)}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold text-foreground truncate">
                          {n.title}
                        </span>
                        {!n.read && (
                          <span className="w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                        )}
                      </div>
                      <p className="text-[11px] text-muted-foreground mt-0.5 line-clamp-2">
                        {n.message}
                      </p>
                      <span className="text-[10px] text-muted-foreground/60 mt-1 block">
                        {new Date(n.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
