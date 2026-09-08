/**
 * HealthConnect AI - Utility Functions
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combine class names with tailwind-merge
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Format date to localized string
 */
export function formatDate(
  date?: string | Date,
  options?: Intl.DateTimeFormatOptions,
): string {
  if (!date) return '—';
  const parsed = typeof date === 'string'
    ? new Date(date.length === 10 ? `${date}T12:00:00` : date)
    : date;
  
  if (Number.isNaN(parsed.getTime())) return String(date);
  
  return parsed.toLocaleDateString(
    'en-US',
    options ?? { month: 'short', day: 'numeric', year: 'numeric' },
  );
}

/**
 * Format relative time (e.g., "5m ago", "2h ago", "3d ago")
 */
export function formatRelative(date?: string | Date): string {
  if (!date) return '';
  
  const parsed = typeof date === 'string' ? new Date(date) : date;
  if (Number.isNaN(parsed.getTime())) return '';
  
  const diff = Date.now() - parsed.getTime();
  const minutes = Math.max(1, Math.floor(diff / 60000));
  
  if (minutes < 60) return `${minutes}m ago`;
  if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
  if (minutes < 10080) return `${Math.floor(minutes / 1440)}d ago`;
  return formatDate(parsed);
}

/**
 * Format time (e.g., "2:30 PM")
 */
export function formatTime(date?: string | Date): string {
  if (!date) return '';
  const parsed = typeof date === 'string' ? new Date(date) : date;
  if (Number.isNaN(parsed.getTime())) return '';
  
  return parsed.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });
}

/**
 * Get initials from name
 */
export function getInitials(firstName?: string, lastName?: string): string {
  const first = firstName?.[0] ?? '';
  const last = lastName?.[0] ?? '';
  return `${first}${last}`.toUpperCase() || 'HC';
}

/**
 * Truncate string
 */
export function truncateString(text: string, maxLength: number = 100): string {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength - 3)}...`;
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => void>(
  func: T,
  wait: number,
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Generate unique ID
 */
export function generateId(prefix: string = ''): string {
  const random = Math.random().toString(36).slice(2, 10).toUpperCase();
  return prefix ? `${prefix}-${random}` : random;
}

/**
 * Sleep utility
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Check if value is empty
 */
export function isEmpty(value: unknown): boolean {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim() === '';
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
}

/**
 * Safe JSON parse
 */
export function safeJsonParse<T>(json: string, fallback: T): T {
  try {
    return JSON.parse(json) as T;
  } catch {
    return fallback;
  }
}

/**
 * Clamp number between min and max
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/**
 * Calculate percentage
 */
export function percentage(part: number, total: number): number {
  if (total === 0) return 0;
  return Math.round((part / total) * 100);
}

/**
 * Group array by key
 */
export function groupBy<T>(array: T[], key: keyof T): Record<string, T[]> {
  return array.reduce((acc, item) => {
    const groupKey = String(item[key]);
    if (!acc[groupKey]) acc[groupKey] = [];
    acc[groupKey].push(item);
    return acc;
  }, {} as Record<string, T[]>);
}

/**
 * Sort array by date
 */
export function sortByDate<T>(
  array: T[],
  dateKey: keyof T,
  direction: 'asc' | 'desc' = 'desc',
): T[] {
  return [...array].sort((a, b) => {
    const dateA = new Date(a[dateKey] as unknown as string).getTime();
    const dateB = new Date(b[dateKey] as unknown as string).getTime();
    return direction === 'asc' ? dateA - dateB : dateB - dateA;
  });
}