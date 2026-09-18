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

export type AppointmentType =
  | 'general'
  | 'follow_up'
  | 'specialist'
  | 'lab'
  | 'imaging'
  | 'vaccination'
  | 'physical'
  | 'consultation'
  | 'urgent_care'
  | 'telehealth';

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
  // Backend-required
  patient_id: string;
  appointment_type: AppointmentType;
  scheduled_datetime: string;   // ISO 8601, e.g. "2026-09-17T09:00:00"
  duration_minutes?: number;
  reason?: string;
  clinic_location?: string | null;
  notes?: string;
}

/**
 * UI-side form model. The form collects { service, date, time, notes };
 * the hook transforms this into an AppointmentCreate payload before POST.
 */
export interface AppointmentFormData {
  service: string;
  date: string;      // YYYY-MM-DD
  time: string;      // HH:MM
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
  available: boolean;
  doctor_id?: string | null;
  clinician?: string | null;   // optional UI label
  date?: string;               // optional, backend sends at response level
}

export interface AppointmentListParams {
  status?: 'upcoming' | 'past';
  patientId?: string;
  dateFrom?: string;
  dateTo?: string;
  limit?: number;
}