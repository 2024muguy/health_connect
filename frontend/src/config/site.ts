/**
 * HealthConnect AI - Site Configuration
 */

export const siteConfig = {
  name: 'HealthConnect AI',
  shortName: 'HealthConnect',
  description: 'Your care, thoughtfully organized.',
  version: '1.0.0',
  url: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  ogImage: '/images/clinic-hero.jpg',
  links: {
    github: 'https://github.com/yourusername/healthconnect-ai',
    twitter: 'https://twitter.com/healthconnect',
  },
  clinic: {
    name: 'HealthConnect Clinic',
    address: '123 Main Street, Suite 100, Springfield, IL 62701',
    phone: '(555) 123-4567',
    email: 'care@healthconnect.com',
  },
  features: {
    chat: true,
    appointments: true,
    analytics: false,
    notifications: true,
  },
} as const;

export type SiteConfig = typeof siteConfig;