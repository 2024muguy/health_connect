'use client';

import Link from 'next/link';
import { Gift, ArrowRight } from 'lucide-react';

export function PromoPreview() {
  return (
    <div className="panel p-4 bg-primary/5 border border-primary/20">
      <div className="flex items-center justify-between mb-3">
        <strong className="text-sm flex items-center gap-2">
          <Gift size={14} className="text-primary" />
          This week
        </strong>
        <Link
          href="/clinic#offers"
          className="text-[11px] text-primary hover:underline flex items-center gap-1"
        >
          All offers <ArrowRight size={11} />
        </Link>
      </div>

      <div className="text-xs">
        <div className="text-[10px] font-semibold text-primary mb-1">
          ✨ Free Blood Pressure Screening
        </div>
        <p className="text-[11px] text-muted-foreground">
          Walk in every Saturday in October for a complimentary BP check.
        </p>
        <Link
          href="/appointments/new"
          className="mt-3 inline-flex items-center gap-1 text-[11px] font-medium text-primary hover:underline"
        >
          Book a slot <ArrowRight size={11} />
        </Link>
      </div>
    </div>
  );
}
