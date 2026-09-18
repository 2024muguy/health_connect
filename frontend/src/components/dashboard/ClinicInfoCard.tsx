'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Clock, MapPin, Phone, Mail, Stethoscope, ArrowRight } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface ClinicInfo {
  name: string;
  description: string;
  founded?: number;
}

export function ClinicInfoCard() {
  const [info, setInfo] = useState<ClinicInfo | null>(null);
  const [services, setServices] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [infoRes, servicesRes] = await Promise.all([
          apiClient.get<any>('/clinic/info').catch(() => null),
          apiClient.get<any>('/clinic/services').catch(() => null),
        ]);

        if (infoRes) {
          setInfo({
            name: infoRes.name || 'HealthConnect Clinic',
            description: infoRes.description || '',
            founded: infoRes.founded,
          });
        }

        if (servicesRes) {
          const list = Array.isArray(servicesRes)
            ? servicesRes
            : servicesRes?.services ?? [];
          setServices(
            list.map((s: any) => (typeof s === 'string' ? s : s?.name)).filter(Boolean)
          );
        }
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="panel p-6">
        <div className="animate-pulse space-y-3">
          <div className="h-4 w-32 bg-muted rounded" />
          <div className="h-3 w-48 bg-muted rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className="panel p-4 md:p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Stethoscope size={18} className="text-primary" />
            {info?.name || 'HealthConnect Clinic'}
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            {info?.description || 'Comprehensive healthcare services for the community'}
          </p>
        </div>
        <Link
          href="/clinic"
          className="text-xs font-medium text-primary hover:underline flex items-center gap-1"
        >
          Details <ArrowRight size={12} />
        </Link>
      </div>

      {/* Contact info */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <MapPin size={14} className="text-primary flex-shrink-0" />
          <span>14 Wellness Avenue, Central District</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Clock size={14} className="text-primary flex-shrink-0" />
          <span>Mon–Fri 8AM–6PM • Sat 9AM–2PM</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Phone size={14} className="text-primary flex-shrink-0" />
          <span>+254 700 000 000</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Mail size={14} className="text-primary flex-shrink-0" />
          <span>care@healthconnect.com</span>
        </div>
      </div>

      {/* Services */}
      {services.length > 0 && (
        <div>
          <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground mb-2">
            Services offered ({services.length})
          </div>
          <div className="flex flex-wrap gap-1.5">
            {services.slice(0, 8).map((s, i) => (
              <span
                key={i}
                className="text-[11px] px-2 py-1 rounded-md bg-muted/60 text-foreground"
              >
                {s}
              </span>
            ))}
            {services.length > 8 && (
              <Link
                href="/clinic"
                className="text-[11px] px-2 py-1 rounded-md bg-primary/10 text-primary font-medium"
              >
                +{services.length - 8} more
              </Link>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
