/**
 * HealthConnect AI - Appointment Store (Zustand)
 */

import { create } from 'zustand';
import type { Appointment, AppointmentAvailability } from '@/types';

interface AppointmentState {
  appointments: Appointment[];
  upcomingAppointments: Appointment[];
  pastAppointments: Appointment[];
  availability: AppointmentAvailability[];
  selectedDate: string;
  selectedService: string;
  selectedTime: string;
  isLoading: boolean;
  error: string | null;
  
  setAppointments: (appointments: Appointment[]) => void;
  addAppointment: (appointment: Appointment) => void;
  updateAppointment: (id: string, updates: Partial<Appointment>) => void;
  removeAppointment: (id: string) => void;
  setAvailability: (availability: AppointmentAvailability[]) => void;
  setSelectedDate: (date: string) => void;
  setSelectedService: (service: string) => void;
  setSelectedTime: (time: string) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  resetBooking: () => void;
}

export const useAppointmentStore = create<AppointmentState>((set) => ({
  appointments: [],
  upcomingAppointments: [],
  pastAppointments: [],
  availability: [],
  selectedDate: '',
  selectedService: '',
  selectedTime: '',
  isLoading: false,
  error: null,
  
  setAppointments: (appointments) =>
    set({
      appointments,
      upcomingAppointments: appointments.filter(
        (a) => a.status === 'scheduled' || a.status === 'confirmed' || a.status === 'pending',
      ),
      pastAppointments: appointments.filter(
        (a) => a.status === 'completed' || a.status === 'cancelled' || a.status === 'no_show',
      ),
    }),
  
  addAppointment: (appointment) =>
    set((state) => ({
      appointments: [...state.appointments, appointment],
      upcomingAppointments: [...state.upcomingAppointments, appointment],
    })),
  
  updateAppointment: (id, updates) =>
    set((state) => ({
      appointments: state.appointments.map((a) =>
        a.id === id ? { ...a, ...updates } : a,
      ),
      upcomingAppointments: state.upcomingAppointments.map((a) =>
        a.id === id ? { ...a, ...updates } : a,
      ),
      pastAppointments: state.pastAppointments.map((a) =>
        a.id === id ? { ...a, ...updates } : a,
      ),
    })),
  
  removeAppointment: (id) =>
    set((state) => ({
      appointments: state.appointments.filter((a) => a.id !== id),
      upcomingAppointments: state.upcomingAppointments.filter((a) => a.id !== id),
      pastAppointments: state.pastAppointments.filter((a) => a.id !== id),
    })),
  
  setAvailability: (availability) => set({ availability }),
  setSelectedDate: (date) => set({ selectedDate: date }),
  setSelectedService: (service) => set({ selectedService: service }),
  setSelectedTime: (time) => set({ selectedTime: time }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  
  resetBooking: () =>
    set({
      selectedDate: '',
      selectedService: '',
      selectedTime: '',
      availability: [],
    }),
}));