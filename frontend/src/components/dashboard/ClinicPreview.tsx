'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Clock, MapPin, ArrowRight } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export function ClinicPreview() {
  const [services, setServices] = useState<string[]>([]);

  useEffect(() => {
    apiClient
      .get<any>('/clinic/services')
      .then((res) => {
        const list = Array.isArray(res) ? res : res?.services ?? [];
        setServices(list.map((s: any) => (typeof s === 'string' ? s : s?.name)).filter(Boolean));
      })
      .catch(() => {});
  }, []);

  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between mb-3">
        <strong className="text-sm">Clinic</strong>
        <Link
          href="/clinic"
          className="text-[11px] text-primary hover:underline flex items-center gap-1"
        >
          Details <ArrowRight size={11} />
        </Link>
      </div>

      <div className="space-y-2 text-xs text-muted-foreground">
        <div className="flex items-start gap-2">
          <MapPin size={13} className="text-primary mt-0.5 flex-shrink-0" />
          <span>14 Wellness Avenue, Central District</span>
        </div>
        <div className="flex items-start gap-2">
          <Clock size={13} className="text-primary mt-0.5 flex-shrink-0" />
          <span>Mon–Fri 8AM–6PM · Sat 9AM–2PM</span>
        </div>
      </div>

      {services.length > 0 && (
        <div className="mt-3 pt-3 border-t border-border/50">
          <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground mb-2">
            {services.length} services
          </div>
          <div className="flex flex-wrap gap-1">
            {services.slice(0, 3).map((s, i) => (
              <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-muted/60">
                {s}
              </span>
            ))}
            {services.length > 3 && (
              <span className="text-[10px] px-2 py-0.5 rounded bg-primary/10 text-primary">
                +{services.length - 3}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
