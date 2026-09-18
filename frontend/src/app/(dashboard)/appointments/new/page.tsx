/**
 * HealthConnect AI - New Appointment Page
 * Multi-step appointment booking
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { useAppointments } from '@/hooks/useAppointments';
import { AppointmentForm } from '@/components/appointment/AppointmentForm';
import { useToast } from '@/hooks/useToast';
import { clinicApi } from '@/lib/api';
import type { ClinicService } from '@/types';

const SERVICE_DURATIONS: Record<string, number> = {
  'General outpatient consultations': 30,
  'Follow-up consultations': 20,
  'Selected specialist consultations': 45,
  'Diagnostic and routine laboratory services': 15,
  'Preventive health and wellness consultations': 30,
};

const SERVICE_DESCRIPTIONS: Record<string, string> = {
  'General outpatient consultations': 'Initial consultation with a general practitioner.',
  'Follow-up consultations': 'Follow-up visit for ongoing care.',
  'Selected specialist consultations': 'Specialist visit (by appointment only).',
  'Diagnostic and routine laboratory services': 'Lab tests and diagnostics.',
  'Preventive health and wellness consultations': 'Wellness check and preventive care.',
};

function normalizeService(raw: any, index: number): { id: string; name: string; description: string; duration: number } {
  if (typeof raw === 'string') {
    return {
      id: `svc-${index}-${raw.toLowerCase().replace(/\s+/g, '-').slice(0, 30)}`,
      name: raw,
      description: SERVICE_DESCRIPTIONS[raw] || '',
      duration: SERVICE_DURATIONS[raw] || 30,
    };
  }
  return {
    id: raw?.id ?? `svc-${index}`,
    name: raw?.name ?? String(raw),
    description: raw?.description ?? '',
    duration: raw?.duration ?? 30,
  };
}


export default function NewAppointmentPage() {
  const router = useRouter();
  const { toast } = useToast();
  const {
    availability,
    loadAvailability,
    bookAppointment,
    isLoading,
  } = useAppointments();

  const [services, setServices] = useState<ClinicService[]>([]);
  const [selectedDate, setSelectedDate] = useState(() => {
    const tomorrow = new Date(Date.now() + 86400000);
    return tomorrow.toISOString().slice(0, 10);
  });
  const [selectedService, setSelectedService] = useState('');

  useEffect(() => {
    const loadServices = async () => {
      try {
        const data = await clinicApi.getServices();
        const rawList: any[] = Array.isArray(data)
          ? data
          : ((data as any)?.services ?? []);
        const list: ClinicService[] = rawList.map((s, i) => normalizeService(s, i) as any);
        setServices(list);
      } catch {
        toast('Failed to load services.', 'error');
      }
    };
    loadServices();
  }, [toast]);

  useEffect(() => {
    if (selectedDate) {
      loadAvailability(selectedDate, selectedService || undefined);
    }
  }, [selectedDate, selectedService, loadAvailability]);

  const handleDateChange = (date: string) => {
    setSelectedDate(date);
  };

  const handleServiceChange = (service: string) => {
    setSelectedService(service);
  };

  const handleSubmit = async (data: any) => {
    const appointment = await bookAppointment(data);
    if (appointment) {
      router.push(`/appointments/${appointment.id}`);
    }
  };

  return (
    <>
      <Link href="/appointments" className="back-link" data-testid="link-back">
        <ArrowLeft size={15} />
        Back to appointments
      </Link>

      <div className="mb-8">
        <p className="eyebrow">Make time for your health</p>
        <h1 className="page-title">Book an appointment</h1>
        <p className="mt-2 text-sm text-muted-foreground max-w-xl">
          Choose a service, then find a time that feels right.
        </p>
      </div>

      <AppointmentForm
        services={services}
        availability={availability}
        isLoadingAvailability={isLoading}
        onSubmit={handleSubmit}
        isSubmitting={isLoading}
      />
    </>
  );
}