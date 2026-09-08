/**
 * HealthConnect AI - Mobile Navigation Component
 * Bottom navigation for mobile devices
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Home,
  CalendarDays,
  MessageCircle,
  Stethoscope,
  UserRound,
  type LucideIcon,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface MobileNavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

const navItems: MobileNavItem[] = [
  { href: '/dashboard', label: 'Home', icon: Home },
  { href: '/appointments', label: 'Visits', icon: CalendarDays },
  { href: '/chat', label: 'Assistant', icon: MessageCircle },
  { href: '/clinic', label: 'Clinic', icon: Stethoscope },
  { href: '/profile', label: 'Profile', icon: UserRound },
];

interface MobileNavProps {
  className?: string;
}

export function MobileNav({ className }: MobileNavProps) {
  const pathname = usePathname();

  const isActive = (href: string): boolean => {
    if (href === '/dashboard') return pathname === '/dashboard';
    return pathname.startsWith(href);
  };

  return (
    <nav
      className={cn(
        'fixed bottom-0 left-0 right-0 z-40 md:hidden',
        'bg-card border-t border-border',
        'grid grid-cols-5',
        className,
      )}
    >
      {navItems.map(({ href, label, icon: Icon }) => (
        <Link
          key={href}
          href={href}
          data-testid={`mobile-link-${label.toLowerCase()}`}
          className={cn(
            'flex flex-col items-center gap-1 py-2.5 text-[9px] font-medium transition-colors',
            isActive(href)
              ? 'text-primary'
              : 'text-muted-foreground hover:text-foreground',
          )}
        >
          <Icon
            size={20}
            strokeWidth={isActive(href) ? 2.2 : 1.8}
          />
          <span>{label}</span>
        </Link>
      ))}
    </nav>
  );
}