import type { Metadata, Viewport } from 'next';
import { type ReactNode } from 'react';
import { Providers } from './providers';
// TypeScript may not have declarations for global CSS imports, but Next.js bundles this stylesheet.
// @ts-expect-error Missing declaration for side-effect CSS import.
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'HealthConnect AI - Patient Companion',
    template: '%s | HealthConnect AI',
  },
  description:
    'Your care, thoughtfully organized. Manage appointments, chat with your care assistant, and access clinic information.',
  keywords: ['healthcare', 'appointments', 'clinic', 'patient portal', 'AI assistant'],
  authors: [{ name: 'HealthConnect AI' }],
  icons: {
    icon: '/favicon.ico',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
