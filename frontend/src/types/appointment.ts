/**
 * HealthConnect AI - Appointment Types
 */

export type AppointmentStatus =
  | 'scheduled'
  | 'confirmed'
  | 'checked_in'
  | 'in_progress'
  | 'completed'
  | 'cancelled'
  | 'no_show'
  | 'rescheduled'
  | 'pending';

export interface Appointment {
  id: string;
  appointment_code: string;
  service: string;
  date: string;
  time: string;
  duration: number;
  status: AppointmentStatus;
  clinician: string;
  clinicianRole?: string;
  location: string;
  locationDetail?: string;
  notes?: string;
  reason?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AppointmentCreate {
  service: string;
  date: string;
  time: string;
  duration?: number;
  notes?: string;
}

export interface AppointmentUpdate {
  service?: string;
  date?: string;
  time?: string;
  status?: AppointmentStatus;
  notes?: string;
}

export interface AppointmentAvailability {
  time: string;
  clinician: string;
  available: boolean;
  date: string;
}

export interface AppointmentListParams {
  status?: 'upcoming' | 'past';
  patientId?: string;
  dateFrom?: string;
  dateTo?: string;
  limit?: number;
}