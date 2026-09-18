/**
 * HealthConnect AI - Header Component
 * Topbar with context, search, notifications, and profile
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Menu,
  MessageCircle,
  LogOut,
  Settings,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Avatar } from '@/components/ui/avatar';
import { Dropdown } from '@/components/ui/dropdown';
import { useAuth } from '@/hooks/useAuth';
import { getInitials } from '@/lib/utils';
import { SearchBar } from './SearchBar';
import { NotificationBell } from './NotificationBell';

interface HeaderProps {
  onMenuClick?: () => void;
  className?: string;
}

export function Header({ onMenuClick, className }: HeaderProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

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
      <button
        data-testid="button-open-menu"
        onClick={onMenuClick}
        className="mobile-menu"
        aria-label="Open menu"
      >
        <Menu size={20} />
      </button>

      <div className="topbar-context">
        <span className="topbar-dot" />
        {getContextLabel()}
      </div>

      <div className="topbar-actions">
        <SearchBar />
        <NotificationBell />

        <Link
          href="/chat"
          data-testid="link-topbar-chat"
          className="icon-button"
          aria-label="Open chat"
        >
          <MessageCircle size={18} />
        </Link>

        {/* Profile — the whole chip opens the dropdown, no arrow, no kebab */}
        <Dropdown
          trigger={
            <button
              type="button"
              className="profile-chip hover:bg-muted/60 transition-colors"
              aria-label="Profile menu"
              data-testid="button-profile-menu"
            >
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
            </button>
          }
          items={profileDropdownItems}
          align="right"
        />
      </div>
    </header>
  );
}
