/**
 * HealthConnect AI - Appointments Page
 * List of upcoming and past appointments
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Plus, CalendarDays } from 'lucide-react';
import { useAppointments } from '@/hooks/useAppointments';
import { AppointmentCard } from '@/components/appointment/AppointmentCard';
import { Tabs } from '@/components/ui/tabs';
import { EmptyState } from '@/components/shared/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/hooks/useToast';
import { cn } from '@/lib/utils';

export default function AppointmentsPage() {
  const [activeTab, setActiveTab] = useState<'upcoming' | 'past'>('upcoming');
  const {
    upcomingAppointments,
    pastAppointments,
    isLoading,
    error,
    loadAppointments,
    cancelAppointment,
  } = useAppointments();

  const { toast } = useToast();
  const [cancellingId, setCancellingId] = useState<string | null>(null);

  useEffect(() => {
    loadAppointments(activeTab);
  }, [activeTab, loadAppointments]);

  const handleCancel = async (id: string) => {
    if (!window.confirm('Cancel this appointment?')) return;

    setCancellingId(id);
    try {
      await cancelAppointment(id);
      await loadAppointments('upcoming');
    } catch {
      toast('Failed to cancel appointment.', 'error');
    } finally {
      setCancellingId(null);
    }
  };

  const currentAppointments = activeTab === 'upcoming' ? upcomingAppointments : pastAppointments;

  const tabs = [
    { id: 'upcoming', label: 'Upcoming', count: upcomingAppointments.length },
    { id: 'past', label: 'Past visits', count: pastAppointments.length },
  ];

  return (
    <>
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
        <div>
          <p className="eyebrow">Your care</p>
          <h1 className="page-title">Appointments</h1>
          <p className="mt-2 text-sm text-muted-foreground max-w-xl">
            Keep track of upcoming visits and look back at where you have been.
          </p>
        </div>
        <Link
          href="/appointments/new"
          className="button button-primary"
          data-testid="link-book-appointment"
        >
          <Plus size={15} />
          Book appointment
        </Link>
      </div>

      {/* Tabs */}
      <div className="filter-bar">
        <Tabs
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={(id) => setActiveTab(id as 'upcoming' | 'past')}
          variant="segmented"
        />
        <span className="filter-count">
          {currentAppointments.length} {activeTab === 'upcoming' ? 'scheduled' : 'visits'}
        </span>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="stack-list">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-[80px] w-full" variant="card" />
          ))}
        </div>
      ) : error ? (
        <EmptyState
          title="Could not load appointments"
          text={error}
        />
      ) : currentAppointments.length > 0 ? (
        <div className="stack-list">
          {currentAppointments.map((appointment) => (
            <AppointmentCard
              key={appointment.id}
              appointment={appointment}
              onCancel={() => handleCancel(appointment.id)}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={CalendarDays}
          title={activeTab === 'upcoming' ? 'Your calendar is open' : 'No past visits yet'}
          text={
            activeTab === 'upcoming'
              ? 'Book a visit when you need one. We will keep the details right here.'
              : 'Completed and cancelled visits will appear here.'
          }
          action={
            activeTab === 'upcoming' ? (
              <Link
                href="/appointments/new"
                className="button button-primary"
              >
                <Plus size={15} />
                Book an appointment
              </Link>
            ) : undefined
          }
        />
      )}

      {/* Toast for cancelling */}
      {cancellingId && (
        <div className="toast-note">
          <span className="animate-spin inline-block w-3.5 h-3.5 border-2 border-primary border-t-transparent rounded-full" />
          Cancelling appointment…
        </div>
      )}
    </>
  );
}