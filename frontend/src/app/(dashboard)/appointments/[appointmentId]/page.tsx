/**
 * HealthConnect AI - Appointment Detail Page
 */

'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  UserRound,
  MapPin,
  CalendarClock,
  FileText,
  CircleHelp,
  Check,
} from 'lucide-react';
import { appointmentApi } from '@/lib/api';
import { AppointmentStatus } from '@/components/appointment/AppointmentStatus';
import { StatusPill } from '@/components/ui/badge';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { useToast } from '@/hooks/useToast';
import { formatDate, cn } from '@/lib/utils';
import type { Appointment } from '@/types';

export default function AppointmentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const appointmentId = params?.appointmentId as string;

  const [appointment, setAppointment] = useState<Appointment | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCancelling, setIsCancelling] = useState(false);
  const [cancelled, setCancelled] = useState(false);

  useEffect(() => {
    const loadAppointment = async () => {
      try {
        const data = await appointmentApi.get(appointmentId);
        setAppointment(data);
      } catch {
        toast('Failed to load appointment.', 'error');
      } finally {
        setIsLoading(false);
      }
    };
    loadAppointment();
  }, [appointmentId, toast]);

  const handleCancel = async () => {
    if (!appointment || !window.confirm('Cancel this appointment?')) return;

    setIsCancelling(true);
    try {
      await appointmentApi.cancel(appointmentId, 'Cancelled by patient');
      setCancelled(true);
      setAppointment({ ...appointment, status: 'cancelled' });
      toast('Appointment cancelled.', 'success');
    } catch {
      toast('Failed to cancel appointment.', 'error');
    } finally {
      setIsCancelling(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
        <LoadingSpinner size="lg" label="Loading appointment…" />
      </div>
    );
  }

  if (!appointment) {
    return (
      <div className="text-center py-16">
        <h2 className="text-lg font-semibold text-foreground">Appointment not found</h2>
        <Link href="/appointments" className="text-link mt-4">
          Back to appointments
        </Link>
      </div>
    );
  }

  const effectiveStatus = cancelled ? 'cancelled' : appointment.status;

  return (
    <>
      <Link href="/appointments" className="back-link" data-testid="link-back">
        <ArrowLeft size={15} />
        Back to appointments
      </Link>

      <div className="detail-layout">
        {/* Main content */}
        <div>
          <div className="detail-hero">
            <div className="detail-date">
              <span>{formatDate(appointment.date, { weekday: 'long' })}</span>
              <strong>{formatDate(appointment.date, { day: 'numeric' })}</strong>
              <span>{formatDate(appointment.date, { month: 'long', year: 'numeric' })}</span>
            </div>
            <div>
              <StatusPill status={effectiveStatus} />
              <h1>{appointment.service}</h1>
              <p>
                {appointment.time} · {appointment.duration} minutes
              </p>
            </div>
          </div>

          {/* Appointment Status Timeline */}
          <div className="detail-card mt-4 p-6">
            <AppointmentStatus status={effectiveStatus} />
          </div>

          {/* Details */}
          <div className="detail-card">
            <InfoLine
              icon={UserRound}
              label="Clinician"
              value={`${appointment.clinician}${appointment.clinicianRole ? `, ${appointment.clinicianRole}` : ''}`}
            />
            <InfoLine
              icon={MapPin}
              label="Location"
              value={`${appointment.location}${appointment.locationDetail ? ` · ${appointment.locationDetail}` : ''}`}
            />
            <InfoLine
              icon={CalendarClock}
              label="Date & time"
              value={`${formatDate(appointment.date, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })} at ${appointment.time}`}
            />
            <InfoLine
              icon={FileText}
              label="Notes"
              value={appointment.notes || 'No notes added'}
            />
          </div>
        </div>

        {/* Sidebar */}
        <aside className="detail-side">
          <div className="side-card">
            <h3>Need to make a change?</h3>
            <p>
              If you cannot make this time, cancelling early helps us offer it
              to another patient.
            </p>
            {effectiveStatus !== 'cancelled' && effectiveStatus !== 'completed' && (
              <button
                data-testid="button-cancel-appointment"
                onClick={handleCancel}
                disabled={isCancelling}
                className="button button-danger w-full"
              >
                {isCancelling ? 'Cancelling…' : 'Cancel appointment'}
              </button>
            )}
            {(effectiveStatus === 'cancelled' || cancelled) && (
              <div className="success-callout">
                <Check size={16} />
                This appointment is cancelled
              </div>
            )}
          </div>

          <div className="side-card soft">
            <CircleHelp size={18} />
            <strong>Questions before your visit?</strong>
            <p>Our care assistant can help you prepare.</p>
            <Link href="/chat" className="button button-secondary w-full">
              Ask a question
            </Link>
          </div>
        </aside>
      </div>
    </>
  );
}

function InfoLine({
  icon: Icon,
  label,
  value,
}: {
  icon: any;
  label: string;
  value: string;
}) {
  return (
    <div className="info-line">
      <div className="info-icon">
        <Icon size={17} />
      </div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}