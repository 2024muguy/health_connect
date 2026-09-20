import type { Metadata, Viewport } from 'next';
import { type ReactNode } from 'react';
import { Providers } from './providers';
// Next.js bundles this stylesheet, even when TypeScript lacks a declaration for it.
// @ts-expect-error Global CSS side-effect imports are handled by Next.js.
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
