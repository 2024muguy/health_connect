/**
 * HealthConnect AI - useAppointments Hook
 * Appointment management logic
 */

'use client';

import { useCallback, useState } from 'react';
import { appointmentApi } from '@/lib/api';
import { useAppointmentStore } from '@/stores/appointment-store';
import type { Appointment, AppointmentCreate, AppointmentAvailability } from '@/types';
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
  bookAppointment: (data: AppointmentCreate) => Promise<Appointment | null>;
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
        const data = await appointmentApi.list({ status });
        setAppointments(data);
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
        const data = await appointmentApi.getAvailability({ date, service });
        setAvailability(data as unknown as AppointmentAvailability[]);
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
    async (data: AppointmentCreate): Promise<Appointment | null> => {
      setIsLoadingLocal(true);
      setError(null);

      try {
        const appointment = await appointmentApi.create(data);
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
    isLoading: isLoadingLocal,
    error,
    loadAppointments,
    loadAvailability,
    bookAppointment,
    cancelAppointment,
    rescheduleAppointment,
    clearError,
  };
}