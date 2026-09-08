/**
 * HealthConnect AI - UpcomingAppointments Component
 * Display upcoming appointments in dashboard
 */

'use client';

import Link from 'next/link';
import { CalendarDays, ArrowRight, Clock3, MapPin } from 'lucide-react';
import type { Appointment } from '@/types';
import { formatDate } from '@/lib/utils';
import { StatusPill } from '@/components/ui/badge';
import { EmptyState } from '@/components/shared/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';

interface UpcomingAppointmentsProps {
  appointments: Appointment[];
  isLoading?: boolean;
  maxItems?: number;
  className?: string;
}

export function UpcomingAppointments({
  appointments,
  isLoading = false,
  maxItems = 3,
  className,
}: UpcomingAppointmentsProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 2 }).map((_, i) => (
          <Skeleton key={i} className="h-[80px] w-full" variant="card" />
        ))}
      </div>
    );
  }

  if (appointments.length === 0) {
    return (
      <EmptyState
        icon={CalendarDays}
        title="Nothing scheduled yet"
        text="When you are ready, we can help find a time that works for you."
        action={
          <Link
            href="/appointments/new"
            className="button button-primary"
          >
            Book an appointment
            <ArrowRight size={15} />
          </Link>
        }
      />
    );
  }

  return (
    <div className={`stack-list ${className || ''}`}>
      {appointments.slice(0, maxItems).map((appointment) => (
        <Link
          key={appointment.id}
          href={`/appointments/${appointment.id}`}
          data-testid={`link-appointment-${appointment.id}`}
          className="appointment-card group"
        >
          <div className="date-block">
            <span>{formatDate(appointment.date, { weekday: 'short' })}</span>
            <strong>{formatDate(appointment.date, { day: 'numeric' })}</strong>
            <span>{formatDate(appointment.date, { month: 'short' })}</span>
          </div>
          <div className="appointment-main">
            <div className="flex flex-wrap items-center gap-2">
              <StatusPill status={appointment.status} />
              <span className="micro-label">{appointment.duration} min</span>
            </div>
            <h3>{appointment.service}</h3>
            <p>
              {appointment.clinician}
              {appointment.clinicianRole ? ` · ${appointment.clinicianRole}` : ''}
            </p>
            <div className="appointment-meta">
              <span>
                <Clock3 size={14} />
                {appointment.time}
              </span>
              <span>
                <MapPin size={14} />
                {appointment.location}
              </span>
            </div>
          </div>
          <div className="appointment-actions opacity-0 group-hover:opacity-100 transition-opacity">
            <span className="text-link">
              View details
              <ArrowRight size={14} />
            </span>
          </div>
        </Link>
      ))}
    </div>
  );
}