'use client';

import { useCallback, useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';

export interface Notification {
  id: string;
  type: 'welcome' | 'appointment' | 'promo' | 'emergency' | 'system';
  title: string;
  message: string;
  read: boolean;
  created_at: string;
}

export function useNotifications(pollMs = 30000) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unread, setUnread] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.get<{ notifications: Notification[]; unread: number }>(
        '/notifications'
      );
      setNotifications(data.notifications || []);
      setUnread(data.unread || 0);
    } catch (err) {
      // Silent — user not logged in or endpoint missing
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, pollMs);
    return () => clearInterval(interval);
  }, [load, pollMs]);

  const markRead = useCallback(async (id: string) => {
    try {
      await apiClient.post(`/notifications/${id}/read`);
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
      setUnread((u) => Math.max(0, u - 1));
    } catch {}
  }, []);

  const markAllRead = useCallback(async () => {
    try {
      await apiClient.post('/notifications/read-all');
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
      setUnread(0);
    } catch {}
  }, []);

  return { notifications, unread, isLoading, refresh: load, markRead, markAllRead };
}
