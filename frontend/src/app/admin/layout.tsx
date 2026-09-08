/**
 * HealthConnect AI - Admin Layout
 * Admin panel layout with authentication check
 */

'use client';

import { useState, type ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import {
  LayoutDashboard,
  Users,
  MessageCircle,
  BarChart3,
  ShieldCheck,
  LogOut,
  Menu,
  X,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Avatar } from '@/components/ui/avatar';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { getInitials, cn } from '@/lib/utils';

const adminNavItems = [
  { href: '/admin', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/admin/users', label: 'Users', icon: Users },
  { href: '/admin/escalations', label: 'Escalations', icon: MessageCircle },
  { href: '/admin/analytics', label: 'Analytics', icon: BarChart3 },
];

interface AdminLayoutProps {
  children: ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <LoadingSpinner size="lg" label="Loading admin panel…" />
      </div>
    );
  }

  if (!isAuthenticated) {
    router.replace('/login');
    return null;
  }

  // Check admin role
  const isAdmin = user?.roles?.includes('admin');
  if (!isAdmin) {
    router.replace('/dashboard');
    return null;
  }

  const isActive = (href: string) => {
    if (href === '/admin') return pathname === '/admin';
    return pathname.startsWith(href);
  };

  return (
    <div className="app-frame">
      {/* Admin Sidebar */}
      <aside className={cn('sidebar', sidebarOpen && 'sidebar-open')}>
        <div className="sidebar-brand">
          <div className="brand-mark bg-accent text-accent-foreground">
            <ShieldCheck size={19} strokeWidth={2.5} />
          </div>
          <div>
            <div className="brand-name">HealthConnect</div>
            <div className="brand-sub">admin panel</div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="mobile-close"
            aria-label="Close menu"
          >
            <X size={18} />
          </button>
        </div>

        <div className="sidebar-section-label">Administration</div>
        <nav className="space-y-1">
          {adminNavItems.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn('nav-link', isActive(href) && 'nav-link-active')}
              onClick={() => setSidebarOpen(false)}
            >
              <Icon size={18} strokeWidth={1.8} />
              <span>{label}</span>
            </Link>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <button
            onClick={() => logout()}
            className="nav-link w-full text-left"
          >
            <LogOut size={18} strokeWidth={1.8} />
            <span>Sign out</span>
          </button>
          <div className="sidebar-meta">
            ADMIN PANEL <span>v1.0</span>
          </div>
        </div>
      </aside>

      {sidebarOpen && (
        <button
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close menu"
        />
      )}

      {/* Main Column */}
      <main className="main-column">
        <header className="topbar">
          <button
            onClick={() => setSidebarOpen(true)}
            className="mobile-menu"
            aria-label="Open menu"
          >
            <Menu size={20} />
          </button>
          <div className="topbar-context">
            <span className="topbar-dot" />
            Admin Panel
          </div>
          <div className="topbar-actions">
            <div className="profile-chip">
              <Avatar initials={getInitials(user?.firstName, user?.lastName)} small />
              <span className="hidden sm:block">{user?.firstName}</span>
            </div>
          </div>
        </header>

        <div className="page-wrap">
          {children}
        </div>
      </main>
    </div>
  );
}