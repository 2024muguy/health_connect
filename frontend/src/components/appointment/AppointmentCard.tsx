/**
 * HealthConnect AI - AppointmentCard Component
 * Appointment display card
 */

'use client';

import Link from 'next/link';
import { Clock3, MapPin, ArrowRight, CalendarClock } from 'lucide-react';
import type { Appointment } from '@/types';
import { formatDate, cn } from '@/lib/utils';
import { StatusPill } from '@/components/ui/badge';

interface AppointmentCardProps {
  appointment: Appointment;
  compact?: boolean;
  onCancel?: () => void;
  className?: string;
}

export function AppointmentCard({
  appointment,
  compact = false,
  onCancel,
  className,
}: AppointmentCardProps) {
  return (
    <div
      data-testid={`card-appointment-${appointment.id}`}
      className={cn('appointment-card', compact && 'p-4', className)}
    >
      <div className="date-block">
        <span>{formatDate(appointment.date, { weekday: 'short' })}</span>
        <strong>{formatDate(appointment.date, { day: 'numeric' })}</strong>
        <span>{formatDate(appointment.date, { month: 'short' })}</span>
      </div>

      <div className="appointment-main">
        <div className="flex flex-wrap items-center gap-2">
          <StatusPill status={appointment.status} />
          <span className="micro-label">
            <CalendarClock size={11} className="inline mr-1" />
            {appointment.duration} min
          </span>
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

      {!compact && (
        <div className="appointment-actions">
          <Link
            href={`/appointments/${appointment.id}`}
            className="button button-secondary"
            data-testid={`link-appointment-detail-${appointment.id}`}
          >
            View details
            <ArrowRight size={14} />
          </Link>
          {onCancel &&
            appointment.status !== 'cancelled' &&
            appointment.status !== 'completed' && (
              <button
                data-testid={`button-cancel-${appointment.id}`}
                onClick={onCancel}
                className="text-button text-destructive hover:text-destructive/80"
              >
                Cancel
              </button>
            )}
        </div>
      )}
    </div>
  );
}