/**
 * HealthConnect AI - Header Component
 * Topbar with context, notifications, and profile
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Menu,
  MessageCircle,
  ChevronDown,
  Bell,
  Search,
  LogOut,
  Settings,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Avatar } from '@/components/ui/avatar';
import { Dropdown } from '@/components/ui/dropdown';
import { useAuth } from '@/hooks/useAuth';
import { getInitials } from '@/lib/utils';

interface HeaderProps {
  onMenuClick?: () => void;
  className?: string;
}

export function Header({ onMenuClick, className }: HeaderProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [notifications] = useState(2);

  const getContextLabel = (): string => {
    if (pathname.startsWith('/appointments')) return 'Appointments';
    if (pathname.startsWith('/chat')) return 'Care assistant';
    if (pathname.startsWith('/clinic')) return 'Clinic information';
    if (pathname.startsWith('/profile')) return 'Your profile';
    if (pathname.startsWith('/admin')) return 'Admin panel';
    return 'A calm place to manage your care';
  };

  const profileDropdownItems = [
    {
      id: 'profile',
      label: 'My profile',
      icon: <Settings size={14} />,
      onClick: () => {
        window.location.href = '/profile';
      },
    },
    {
      id: 'logout',
      label: 'Sign out',
      icon: <LogOut size={14} />,
      danger: true,
      onClick: () => {
        logout();
      },
    },
  ];

  return (
    <header className={cn('topbar', className)}>
      {/* Mobile menu button */}
      <button
        data-testid="button-open-menu"
        onClick={onMenuClick}
        className="mobile-menu"
        aria-label="Open menu"
      >
        <Menu size={20} />
      </button>

      {/* Context */}
      <div className="topbar-context">
        <span className="topbar-dot" />
        {getContextLabel()}
      </div>

      {/* Actions */}
      <div className="topbar-actions">
        {/* Search (desktop) */}
        <button className="icon-button hidden md:grid" aria-label="Search">
          <Search size={18} />
        </button>

        {/* Notifications */}
        <button className="icon-button" aria-label="Notifications">
          <Bell size={18} />
          {notifications > 0 && (
            <span className="notification-dot" />
          )}
        </button>

        {/* Chat quick link */}
        <Link
          href="/chat"
          data-testid="link-topbar-chat"
          className="icon-button"
          aria-label="Open chat"
        >
          <MessageCircle size={18} />
          <span className="notification-dot" />
        </Link>

        {/* Profile */}
        <Dropdown
          trigger={
            <div className="profile-chip">
              <Avatar
                initials={
                  user
                    ? getInitials(user.firstName || '', user.lastName || '')
                    : 'HC'
                }
                small
              />
              <span className="hidden sm:block">
                {user ? `${user.firstName || user.full_name || 'My profile'}` : 'My profile'}
              </span>
              <ChevronDown size={14} className="text-muted-foreground" />
            </div>
          }
          items={profileDropdownItems}
          align="right"
        />
      </div>
    </header>
  );
}