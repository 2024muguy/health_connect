/**
 * HealthConnect AI - Breadcrumbs Component
 * Navigation breadcrumbs
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronRight, Home } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
  className?: string;
}

export function Breadcrumbs({ items, className }: BreadcrumbsProps) {
  const pathname = usePathname();

  const generateItems = (): BreadcrumbItem[] => {
    if (items) return items;

    const segments = pathname.split('/').filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [
      { label: 'Home', href: '/dashboard' },
    ];

    let currentPath = '';
    for (const segment of segments) {
      currentPath += `/${segment}`;
      const label = segment
        .replace(/[-_]/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase());

      breadcrumbs.push({
        label,
        href: currentPath,
      });
    }

    return breadcrumbs;
  };

  const breadcrumbItems = generateItems();

  return (
    <nav
      aria-label="Breadcrumbs"
      className={cn('flex items-center gap-1.5', className)}
    >
      {breadcrumbItems.map((item, index) => {
        const isLast = index === breadcrumbItems.length - 1;

        return (
          <div key={index} className="flex items-center gap-1.5">
            {index > 0 && (
              <ChevronRight
                size={13}
                className="text-muted-foreground/50"
              />
            )}
            {isLast ? (
              <span className="text-[11px] font-semibold text-foreground">
                {item.label}
              </span>
            ) : item.href ? (
              <Link
                href={item.href}
                className="text-[11px] text-muted-foreground hover:text-primary transition-colors"
              >
                {index === 0 ? (
                  <span className="flex items-center gap-1">
                    <Home size={13} />
                    {item.label}
                  </span>
                ) : (
                  item.label
                )}
              </Link>
            ) : (
              <span className="text-[11px] text-muted-foreground">
                {item.label}
              </span>
            )}
          </div>
        );
      })}
    </nav>
  );
}