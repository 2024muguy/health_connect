/**
 * HealthConnect AI - Clinic Page
 * Clinic information and services
 */

'use client';

import { useEffect, useState } from 'react';
import {
  MapPin,
  Phone,
  Mail,
  CalendarClock,
  Clock3,
} from 'lucide-react';
import { clinicApi } from '@/lib/api';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/shared/EmptyState';
import type { ClinicInfo, ClinicService } from '@/types';

export default function ClinicPage() {
  const [info, setInfo] = useState<ClinicInfo | null>(null);
  const [services, setServices] = useState<ClinicService[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [infoData, servicesData] = await Promise.all([
          clinicApi.getInfo(),
          clinicApi.getServices(),
        ]);
        setInfo(infoData);
        setServices(servicesData as unknown as ClinicService[]);
      } catch {
        // Handle error
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
        <p className="mt-2 text-sm text-muted-foreground">
          {info.tagline || 'Thoughtful care, close to home.'}
        </p>
      </div>

      {/* Clinic Intro */}
      <div className="clinic-intro">
        <div className="clinic-map">
          <div className="map-grid" />
          <div className="map-pin">
            <MapPin size={20} fill="currentColor" />
          </div>
          <span>We are here for you</span>
        </div>

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
        <span className="muted-count">{services.length} ways we can help</span>
      </div>

      <div className="services-grid">
        {services.map((service, index) => (
          <div
            key={service.id}
            data-testid={`card-service-${service.id}`}
            className={`service-card service-accent-${index % 2 + 1}`}
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