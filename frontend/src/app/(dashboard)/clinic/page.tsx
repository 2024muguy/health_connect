/**
 * HealthConnect AI - Clinic Page
 * Full clinic information, services, map, and offers
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  MapPin,
  Phone,
  Mail,
  CalendarClock,
  Clock3,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/shared/EmptyState';
import { ClinicMap } from '@/components/dashboard/ClinicMap';
import { PromoOffers } from '@/components/dashboard/PromoOffers';

const SERVICE_DURATIONS: Record<string, number> = {
  'General outpatient consultations': 30,
  'Follow-up consultations': 20,
  'Selected specialist consultations': 45,
  'Diagnostic and routine laboratory services': 15,
  'Preventive health and wellness consultations': 30,
};

const SERVICE_DESCRIPTIONS: Record<string, string> = {
  'General outpatient consultations': 'Initial consultation with a general practitioner.',
  'Follow-up consultations': 'Follow-up visit for ongoing care.',
  'Selected specialist consultations': 'Specialist visit (by appointment only).',
  'Diagnostic and routine laboratory services': 'Lab tests and diagnostics.',
  'Preventive health and wellness consultations': 'Wellness check and preventive care.',
};

function normalizeService(raw: any, index: number) {
  if (typeof raw === 'string') {
    return {
      id: `svc-${index}`,
      name: raw,
      description: SERVICE_DESCRIPTIONS[raw] || '',
      duration: SERVICE_DURATIONS[raw] || 30,
    };
  }
  return {
    id: raw?.id ?? `svc-${index}`,
    name: raw?.name ?? String(raw),
    description: raw?.description ?? '',
    duration: raw?.duration ?? 30,
  };
}

export default function ClinicPage() {
  const [info, setInfo] = useState<any>(null);
  const [services, setServices] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Auto-scroll to hash anchor (#directions, #offers)
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const scrollToHash = () => {
      const hash = window.location.hash;
      if (!hash) return;
      const id = hash.slice(1);
      const el = document.getElementById(id);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    };

    // Scroll on initial load (give DOM a moment to render)
    const timer = setTimeout(scrollToHash, 300);

    // Also scroll when the hash changes (e.g., clicking again)
    window.addEventListener('hashchange', scrollToHash);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('hashchange', scrollToHash);
    };
  }, []);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [infoRes, servicesRes] = await Promise.all([
          apiClient.get<any>('/clinic/info').catch(() => null),
          apiClient.get<any>('/clinic/services').catch(() => null),
        ]);

        if (infoRes) {
          setInfo({
            name: infoRes.name || 'HealthConnect Clinic',
            tagline: infoRes.description || 'Comprehensive healthcare services for the community',
            address: '14 Wellness Avenue, Central District',
            phone: '+254 700 000 000',
            email: 'care@healthconnect.com',
            hours: 'Mon–Fri 8AM–6PM · Sat 9AM–2PM',
            founded: infoRes.founded,
          });
        }

        if (servicesRes) {
          const raw = Array.isArray(servicesRes) ? servicesRes : servicesRes?.services ?? [];
          setServices(raw.map((s: any, i: number) => normalizeService(s, i)));
        }
      } catch (err) {
        console.error('[clinic] load failed', err);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-[230px] w-full" variant="card" />
        <Skeleton className="h-[154px] w-full" variant="card" />
      </div>
    );
  }

  if (!info) {
    return (
      <EmptyState
        title="Clinic information unavailable"
        text="We could not load clinic details. Please try again later."
      />
    );
  }

  return (
    <>
      <div className="mb-8">
        <p className="eyebrow">The people behind your care</p>
        <h1 className="page-title">{info.name}</h1>
        <p className="mt-2 text-sm text-muted-foreground">{info.tagline}</p>
      </div>

      {/* Contact grid */}
      <div className="clinic-intro">
        <div className="clinic-contact-grid">
          <Contact icon={MapPin} label="Visit us" value={info.address} />
          <Contact icon={Phone} label="Call the clinic" value={info.phone} />
          <Contact icon={Mail} label="Email us" value={info.email} />
          <Contact icon={Clock3} label="Hours" value={info.hours} />
        </div>
      </div>

      {/* Services */}
      <div className="section-heading mt-10 mb-5">
        <h2>Services</h2>
        <span className="muted-count">
          {services.length} ways we can help
        </span>
      </div>

      <div className="services-grid">
        {services.map((service, index) => (
          <div
            key={service.id}
            data-testid={`card-service-${service.id}`}
            className={`service-card service-accent-${(index % 2) + 1}`}
          >
            <div className="service-number">
              {String(index + 1).padStart(2, '0')}
            </div>
            <div>
              <h3>{service.name}</h3>
              <p>{service.description}</p>
              <span className="service-duration">
                <CalendarClock size={14} />
                {service.duration} minutes
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* ============================================================
          DIRECTIONS — full interactive map
          ============================================================ */}
      <div id="directions" className="section-heading mt-12 mb-5">
        <h2>Directions</h2>
        <span className="muted-count">Navigate to Ongata Rongai</span>
      </div>

      <ClinicMap />

      {/* ============================================================
          OFFERS — full promo list
          ============================================================ */}
      <div id="offers" className="section-heading mt-12 mb-5">
        <h2>Special Offers</h2>
        <span className="muted-count">Health programs & promotions</span>
      </div>

      <PromoOffers />
    </>
  );
}

function Contact({
  icon: Icon,
  label,
  value,
}: {
  icon: any;
  label: string;
  value: string;
}) {
  return (
    <div className="contact-item">
      <div className="contact-icon">
        <Icon size={17} />
      </div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}
