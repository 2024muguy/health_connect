'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';

export default function LandingPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        router.replace('/dashboard');
      } else {
        router.replace('/login');
      }
    }
  }, [isAuthenticated, isLoading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-primary flex items-center justify-center">
          <span className="text-primary-foreground text-2xl font-serif">HC</span>
        </div>
        <h1 className="text-2xl font-semibold text-foreground mb-2">
          HealthConnect AI
        </h1>
        <p className="text-sm text-muted-foreground mb-6">
          Your care, thoughtfully organized.
        </p>
        <LoadingSpinner size="lg" />
      </div>
    </div>
  );
}