'use client';

import { Sparkles, Calendar, Gift, Percent, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface Offer {
  id: string;
  title: string;
  description: string;
  badge?: string;
  validUntil?: string;
  cta?: { label: string; href: string };
  variant?: 'primary' | 'accent' | 'success' | 'warning';
}

const DEMO_OFFERS: Offer[] = [
  {
    id: 'free-screening',
    title: 'Free Blood Pressure Screening',
    description: 'Walk in every Saturday in October for a complimentary BP check.',
    badge: 'This Week',
    validUntil: 'Oct 31, 2026',
    variant: 'primary',
    cta: { label: 'Book a slot', href: '/appointments/new' },
  },
  {
    id: 'flu-shot',
    title: 'Flu Shot — 20% Off',
    description: 'Protect your family this season. Discount applied at checkout.',
    badge: 'Limited',
    validUntil: 'Nov 15, 2026',
    variant: 'accent',
    cta: { label: 'Learn more', href: '/clinic' },
  },
  {
    id: 'referral',
    title: 'Refer a Friend — Get KSh 500 Off',
    description: 'Both you and your friend receive a discount on your next visit.',
    variant: 'success',
    cta: { label: 'Invite', href: '/profile' },
  },
];

export function PromoOffers() {
  return (
    <div className="panel p-4 md:p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Gift size={18} className="text-primary" />
            Special Offers
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            Health programs & promotions for you
          </p>
        </div>
        <Sparkles size={16} className="text-muted-foreground" />
      </div>

      <div className="grid gap-3">
        {DEMO_OFFERS.map((offer) => (
          <div
            key={offer.id}
            className={cn(
              'rounded-xl p-4 border transition-colors relative overflow-hidden',
              offer.variant === 'primary' && 'bg-primary/5 border-primary/20',
              offer.variant === 'accent' && 'bg-accent/10 border-accent/20',
              offer.variant === 'success' && 'bg-emerald-500/5 border-emerald-500/20',
              offer.variant === 'warning' && 'bg-amber-500/5 border-amber-500/20',
              !offer.variant && 'bg-muted/50 border-border'
            )}
          >
            {offer.badge && (
              <span className="absolute top-3 right-3 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-primary text-primary-foreground">
                {offer.badge}
              </span>
            )}

            <div className="flex items-start gap-3">
              <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Percent size={16} className="text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold text-foreground">
                  {offer.title}
                </h3>
                <p className="text-xs text-muted-foreground mt-1">
                  {offer.description}
                </p>

                <div className="flex items-center justify-between mt-3">
                  {offer.validUntil && (
                    <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                      <Calendar size={10} /> Valid until {offer.validUntil}
                    </span>
                  )}
                  {offer.cta && (
                    <Link
                      href={offer.cta.href}
                      className="text-xs font-medium text-primary hover:underline flex items-center gap-1"
                    >
                      {offer.cta.label}
                      <ArrowRight size={12} />
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
