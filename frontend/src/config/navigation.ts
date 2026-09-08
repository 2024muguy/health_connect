/**
 * HealthConnect AI - Navigation Configuration
 */

import {
  Home,
  CalendarDays,
  MessageCircle,
  Stethoscope,
  UserRound,
  type LucideIcon,
} from 'lucide-react';

export interface NavigationItem {
  href: string;
  label: string;
  icon: LucideIcon;
  description?: string;
  badge?: number;
  requiresAuth?: boolean;
  adminOnly?: boolean;
}

export const mainNavigation: NavigationItem[] = [
  {
    href: '/dashboard',
    label: 'Overview',
    icon: Home,
    description: 'Your care at a glance',
    requiresAuth: true,
  },
  {
    href: '/appointments',
    label: 'Appointments',
    icon: CalendarDays,
    description: 'Manage your visits',
    requiresAuth: true,
  },
  {
    href: '/chat',
    label: 'Conversations',
    icon: MessageCircle,
    description: 'Talk to your care assistant',
    requiresAuth: true,
    badge: 3,
  },
  {
    href: '/clinic',
    label: 'Clinic & services',
    icon: Stethoscope,
    description: 'Learn about our care',
    requiresAuth: false,
  },
  {
    href: '/profile',
    label: 'My profile',
    icon: UserRound,
    description: 'Your personal information',
    requiresAuth: true,
  },
];

export const adminNavigation: NavigationItem[] = [
  {
    href: '/admin',
    label: 'Admin dashboard',
    icon: Home,
    adminOnly: true,
  },
  {
    href: '/admin/users',
    label: 'Users',
    icon: UserRound,
    adminOnly: true,
  },
  {
    href: '/admin/escalations',
    label: 'Escalations',
    icon: MessageCircle,
    adminOnly: true,
  },
  {
    href: '/admin/analytics',
    label: 'Analytics',
    icon: CalendarDays,
    adminOnly: true,
  },
];

export const quickLinks = [
  {
    href: '/appointments/new',
    label: 'Book appointment',
  },
  {
    href: '/chat',
    label: 'Ask assistant',
  },
  {
    href: '/clinic',
    label: 'Find clinic',
  },
] as const;

export const footerLinks = [
  {
    href: '/clinic',
    label: 'Clinic information',
  },
  {
    href: '/profile',
    label: 'My profile',
  },
  {
    href: '/chat',
    label: 'Care assistant',
  },
] as const;