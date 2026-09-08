import type { Metadata } from 'next';
import { type ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ErrorBoundary } from '@/components/shared/ErrorBoundary';
import { Toaster } from '@/components/ui/toast';
import { TooltipProvider } from '@/components/ui/tooltip';
import './globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

export const metadata: Metadata = {
  title: {
    default: 'HealthConnect AI - Patient Companion',
    template: '%s | HealthConnect AI',
  },
  description: 'Your care, thoughtfully organized. Manage appointments, chat with your care assistant, and access clinic information.',
  keywords: ['healthcare', 'appointments', 'clinic', 'patient portal', 'AI assistant'],
  authors: [{ name: 'HealthConnect AI' }],
  viewport: 'width=device-width, initial-scale=1',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <QueryClientProvider client={queryClient}>
          <TooltipProvider>
            <ErrorBoundary>
              {children}
            </ErrorBoundary>
            <Toaster />
          </TooltipProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}