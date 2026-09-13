/**
 * HealthConnect AI - Dashboard Layout
 * Shared layout with sidebar and header for all dashboard pages
 */

'use client';

import { useEffect, useState, type ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { MobileNav } from '@/components/layout/MobileNav';
import { Footer } from '@/components/layout/Footer';
import { useAuth } from '@/hooks/useAuth';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { ErrorBoundary } from '@/components/shared/ErrorBoundary';
import { cn } from '@/lib/utils';

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, isLoading } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // ✅ Redirect inside useEffect — never during render
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <LoadingSpinner size="lg" label="Loading your care dashboard…" />
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect will happen in the effect above — render nothing meanwhile
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <LoadingSpinner size="lg" label="Redirecting to sign in…" />
      </div>
    );
  }

  return (
    <div className="app-frame">
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="main-column">
        <Header onMenuClick={() => setSidebarOpen(true)} />

        <div className="page-wrap">
          <ErrorBoundary resetKey={pathname}>
            {children}
          </ErrorBoundary>
        </div>

        <Footer />
      </main>

      <MobileNav />
    </div>
  );
}
