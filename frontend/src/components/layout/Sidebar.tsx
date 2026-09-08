/**
 * HealthConnect AI - Sidebar Component
 * Main navigation sidebar with coastal teal styling
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  HeartPulse,
  Home,
  CalendarDays,
  MessageCircle,
  Stethoscope,
  UserRound,
  Sparkles,
  X,
  type LucideIcon,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useHealthCheck } from '@/hooks/useHealthCheck';
import { useAuth } from '@/hooks/useAuth';
import { Logo } from '@/components/shared/Logo';

interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  badge?: number;
}

const navItems: NavItem[] = [
  { href: '/dashboard', label: 'Overview', icon: Home },
  { href: '/appointments', label: 'Appointments', icon: CalendarDays },
  { href: '/chat', label: 'Conversations', icon: MessageCircle, badge: 3 },
  { href: '/clinic', label: 'Clinic & services', icon: Stethoscope },
  { href: '/profile', label: 'My profile', icon: UserRound },
];

interface SidebarProps {
  open?: boolean;
  onClose?: () => void;
  className?: string;
}

export function Sidebar({ open = false, onClose, className }: SidebarProps) {
  const pathname = usePathname();
  const { user } = useAuth();
  const health = useHealthCheck();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (href: string): boolean => {
    if (href === '/dashboard') return pathname === '/dashboard';
    return pathname.startsWith(href);
  };

  const isSidebarOpen = open || mobileOpen;

  return (
    <>
      {/* Mobile overlay */}
      {isSidebarOpen && (
        <button
          data-testid="button-menu-overlay"
          className="sidebar-overlay"
          onClick={() => {
            setMobileOpen(false);
            onClose?.();
          }}
          aria-label="Close menu"
        />
      )}

      <aside
        className={cn(
          'sidebar',
          isSidebarOpen && 'sidebar-open',
          className,
        )}
      >
        {/* Brand */}
        <div className="sidebar-brand">
          <div className="brand-mark">
            <HeartPulse size={19} strokeWidth={2.5} />
          </div>
          <div>
            <div className="brand-name">HealthConnect</div>
            <div className="brand-sub">patient companion</div>
          </div>
          <button
            data-testid="button-close-menu"
            onClick={() => {
              setMobileOpen(false);
              onClose?.();
            }}
            className="mobile-close"
            aria-label="Close menu"
          >
            <X size={18} />
          </button>
        </div>

        {/* Navigation */}
        <div className="sidebar-section-label">Your care</div>
        <nav className="space-y-1">
          {navItems.map(({ href, label, icon: Icon, badge }) => (
            <Link
              key={href}
              href={href}
              data-testid={`link-${label.toLowerCase().replaceAll(' ', '-')}`}
              onClick={() => {
                setMobileOpen(false);
                onClose?.();
              }}
              className={cn(
                'nav-link',
                isActive(href) && 'nav-link-active',
              )}
            >
              <Icon size={18} strokeWidth={1.8} />
              <span>{label}</span>
              {badge !== undefined && (
                <span className="nav-indicator">{badge}</span>
              )}
            </Link>
          ))}
        </nav>

        {/* Bottom section */}
        <div className="sidebar-bottom">
          <div className="sidebar-help">
            <div className="help-orb">
              <Sparkles size={17} />
            </div>
            <div>
              <strong>Have a question?</strong>
              <span>Ask your care assistant</span>
            </div>
          </div>

          <div className="connection">
            <span
              className={cn(
                'connection-dot',
                health.isError ? 'is-error' : '',
              )}
            />
            {health.isLoading
              ? 'Connecting…'
              : health.isError
                ? 'Connection issue'
                : 'Care network online'}
          </div>

          <div className="sidebar-meta">
            HEALTHCONNECT AI <span>v1.0</span>
          </div>
        </div>
      </aside>
    </>
  );
}

// Health check hook placeholder (would be imported from API)
function useHealthCheckFallback() {
  return { isLoading: false, isError: false };
}