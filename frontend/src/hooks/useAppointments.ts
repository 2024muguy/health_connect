import { getAccessToken } from '@/lib/api-client';
/**
 * HealthConnect AI - useAppointments Hook
 * Appointment management logic
 */

'use client';

import { useCallback, useState } from 'react';
import { appointmentApi } from '@/lib/api';
import { useAppointmentStore } from '@/stores/appointment-store';
import type { Appointment, AppointmentCreate, AppointmentAvailability, AppointmentFormData } from '@/types';
import { useToast } from './useToast';

interface UseAppointmentsReturn {
  appointments: Appointment[];
  upcomingAppointments: Appointment[];
  pastAppointments: Appointment[];
  availability: AppointmentAvailability[];
  isLoading: boolean;
  error: string | null;
  loadAppointments: (status?: 'upcoming' | 'past') => Promise<void>;
  loadAvailability: (date: string, service?: string) => Promise<void>;
  bookAppointment: (data: AppointmentFormData) => Promise<Appointment | null>;
  cancelAppointment: (id: string, reason?: string) => Promise<void>;
  rescheduleAppointment: (id: string, newDatetime: string) => Promise<void>;
  clearError: () => void;
}

export function useAppointments(): UseAppointmentsReturn {
  const {
    appointments,
    upcomingAppointments,
    pastAppointments,
    availability,
    setAppointments,
    addAppointment,
    updateAppointment,
    removeAppointment,
    setAvailability,
    setLoading,
    setError: setStoreError,
  } = useAppointmentStore();

  const [isLoading, setIsLoadingLocal] = useState(false);
  const [error, setErrorLocal] = useState<string | null>(null);
  const { toast } = useToast();

  const setError = useCallback(
    (message: string | null) => {
      setErrorLocal(message);
      setStoreError(message);
    },
    [setStoreError],
  );

  const loadAppointments = useCallback(
    async (status?: 'upcoming' | 'past') => {
      setIsLoadingLocal(true);
      setLoading(true);
      setError(null);

      try {
        const data: any = await appointmentApi.list({ status });
        setAppointments(Array.isArray(data) ? data : (data)?.appointments ?? []);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load appointments.';
        setError(message);
      } finally {
        setIsLoadingLocal(false);
        setLoading(false);
      }
    },
    [setAppointments, setLoading, setError],
  );

  const loadAvailability = useCallback(
    async (date: string, service?: string) => {
      setLoading(true);
      setError(null);

      try {
        const data: any = await appointmentApi.getAvailability({ date, service });
        setAvailability(
          Array.isArray(data)
            ? data
            : (data as any)?.available_slots
              ?? (data as any)?.availability
              ?? (data as any)?.slots
              ?? [],
        );
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load availability.';
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    [setAvailability, setLoading, setError],
  );

  const bookAppointment = useCallback(
    async (data: AppointmentFormData): Promise<Appointment | null> => {
      setIsLoadingLocal(true);
      setError(null);

      try {
        const patientId = await resolvePatientId();
        const payload: AppointmentCreate = {
          patient_id: patientId,
          appointment_type: mapServiceToAppointmentType(data.service),
          scheduled_datetime: combineDateAndTime(data.date, data.time),
          duration_minutes: data.duration,
          reason: data.service,
          notes: data.notes,
        };

        const appointment = await appointmentApi.create(payload);
        addAppointment(appointment);
        toast('Appointment booked successfully!', 'success');
        return appointment;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to book appointment.';
        setError(message);
        toast(message, 'error');
        return null;
      } finally {
        setIsLoadingLocal(false);
      }
    },
    [addAppointment, toast, setError],
  );

  const cancelAppointment = useCallback(
    async (id: string, reason?: string) => {
      setIsLoadingLocal(true);
      setError(null);

      try {
        await appointmentApi.cancel(id, reason);
        updateAppointment(id, { status: 'cancelled' });
        toast('Appointment cancelled.', 'success');
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to cancel appointment.';
        setError(message);
        toast(message, 'error');
        throw err;
      } finally {
        setIsLoadingLocal(false);
      }
    },
    [updateAppointment, toast, setError],
  );

  const rescheduleAppointment = useCallback(
    async (id: string, newDatetime: string) => {
      setIsLoadingLocal(true);
      setError(null);

      try {
        await appointmentApi.reschedule(id, newDatetime);
        updateAppointment(id, { status: 'rescheduled' });
        toast('Appointment rescheduled.', 'success');
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to reschedule appointment.';
        setError(message);
        toast(message, 'error');
        throw err;
      } finally {
        setIsLoadingLocal(false);
      }
    },
    [updateAppointment, toast, setError],
  );

  const clearError = useCallback(() => setError(null), [setError]);

  return {
    appointments,
    upcomingAppointments,
    pastAppointments,
    availability,
    isLoading,
    error,
    loadAppointments,
    loadAvailability,
    bookAppointment,
    cancelAppointment,
    rescheduleAppointment,
    clearError,
  };
}

// ============================================
// Helpers — UI form → backend payload
// ============================================

function combineDateAndTime(date: string, time: string): string {
  // date = "2026-09-17", time = "09:00"  ->  "2026-09-17T09:00:00"
  const normalizedTime = time.length === 5 ? `${time}:00` : time;
  return `${date}T${normalizedTime}`;
}

function mapServiceToAppointmentType(service: string): AppointmentCreate['appointment_type'] {
  const s = (service || '').toLowerCase();

  // Match the backend enum:
  //   general | follow_up | specialist | lab | imaging | vaccination
  //   | physical | consultation | urgent_care | telehealth
  if (s.includes('follow')) return 'follow_up';
  if (s.includes('special') || s.includes('cardio') || s.includes('dermat')
      || s.includes('neuro') || s.includes('ortho')) return 'specialist';
  if (s.includes('lab') || s.includes('blood') || s.includes('test')) return 'lab';
  if (s.includes('imaging') || s.includes('x-ray') || s.includes('xray')
      || s.includes('mri') || s.includes('ct') || s.includes('scan')
      || s.includes('ultrasound')) return 'imaging';
  if (s.includes('vaccin') || s.includes('immuniz')) return 'vaccination';
  if (s.includes('physical') || s.includes('checkup') || s.includes('check-up')
      || s.includes('annual')) return 'physical';
  if (s.includes('consult') || s.includes('internal') || s.includes('medicine')
      || s.includes('pediatr') || s.includes('gyn')) return 'consultation';
  if (s.includes('urgent') || s.includes('emergency')) return 'urgent_care';
  if (s.includes('tele') || s.includes('virtual') || s.includes('online')) return 'telehealth';
  if (s.includes('general') || s.includes('outpatient') || s.includes('primary'))
      return 'general';
  return 'general';   // safe default that always validates
}

/**
 * Return the current patient's ID. Uses the auth store / profile if available,
 * otherwise falls back to a per-browser demo UUID stored in localStorage.
 * Replace with a real auth-derived ID when the login flow exposes one.
 */
async function resolvePatientId(): Promise<string> {
  if (typeof window === 'undefined') return '';

  // 1) Cache first (fastest path)
  const cached = window.localStorage.getItem('hc_patient_id');
  if (cached && /^[0-9a-f-]{36}$/i.test(cached)) return cached;

  // 2) Ask the backend using the shared apiClient so the correct
  //    auth header is attached automatically.
  const { apiClient } = await import('@/lib/api-client');
  const me: any = await apiClient.get('/auth/me');
  console.log('[resolvePatientId] /auth/me =', me);

  const pid = me?.patient_id;
  if (!pid || !/^[0-9a-f-]{36}$/i.test(pid)) {
    throw new Error(
      'Your account has no linked patient profile. Please sign out and sign in again.'
    );
  }

  window.localStorage.setItem('hc_patient_id', pid);
  return pid;
}
