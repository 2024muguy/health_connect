/**
 * HealthConnect AI - AppointmentForm Component
 * Multi-step appointment booking form
 */

'use client';

import { useState, type FormEvent } from 'react';
import { Check, Stethoscope, Heart, ShieldCheck } from 'lucide-react';
import type { AppointmentCreate, AppointmentAvailability } from '@/types';
import { formatDate, cn } from '@/lib/utils';
import { LoadingButton } from '@/components/ui/button';
import { SkeletonBlock } from '@/components/ui/spinner';

interface AppointmentFormProps {
  services: Array<{ id: string; name: string; description: string; duration: number }>;
  availability: AppointmentAvailability[];
  isLoadingAvailability?: boolean;
  onSubmit: (data: AppointmentCreate) => Promise<void>;
  isSubmitting?: boolean;
  className?: string;
}

export function AppointmentForm({
  services,
  availability,
  isLoadingAvailability = false,
  onSubmit,
  isSubmitting = false,
  className,
}: AppointmentFormProps) {
  const [service, setService] = useState('');
  const [date, setDate] = useState(() => {
    const tomorrow = new Date(Date.now() + 86400000);
    return tomorrow.toISOString().slice(0, 10);
  });
  const [time, setTime] = useState('');
  const [notes, setNotes] = useState('');

  const chosenService = services.find((s) => s.name === service);
  const availableSlots = availability.filter((slot) => slot.available);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!service || !time) return;

    onSubmit({
      service,
      date,
      time,
      duration: chosenService?.duration,
      notes: notes || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className={cn('booking-layout', className)}>
      <div className="booking-form">
        {/* Step 1: Service */}
        <div className="form-step">
          <span className="step-number">01</span>
          <div className="step-content">
            <label htmlFor="service">What can we help with?</label>
            <p>Choose the kind of care you need.</p>
            <select
              id="service"
              data-testid="select-service"
              value={service}
              onChange={(e) => {
                setService(e.target.value);
                setTime('');
              }}
            >
              <option value="">Select a service</option>
              {services.map((item) => (
                <option key={item.id} value={item.name}>
                  {item.name} · {item.duration} min
                </option>
              ))}
            </select>
            {chosenService && (
              <div className="service-note">
                <Stethoscope size={15} />
                {chosenService.description}
              </div>
            )}
          </div>
        </div>

        {/* Step 2: Date & Time */}
        <div className="form-step">
          <span className="step-number">02</span>
          <div className="step-content">
            <label htmlFor="date">When works for you?</label>
            <p>Available times update as you explore dates.</p>
            <input
              id="date"
              data-testid="input-date"
              type="date"
              min={new Date(Date.now() + 86400000).toISOString().slice(0, 10)}
              value={date}
              onChange={(e) => {
                setDate(e.target.value);
                setTime('');
              }}
            />
            <div className="time-grid mt-4">
              {isLoadingAvailability ? (
                <>
                  <SkeletonBlock className="h-11" />
                  <SkeletonBlock className="h-11" />
                  <SkeletonBlock className="h-11" />
                  <SkeletonBlock className="h-11" />
                  <SkeletonBlock className="h-11" />
                  <SkeletonBlock className="h-11" />
                </>
              ) : availableSlots.length ? (
                availableSlots.map((slot) => (
                  <button
                    type="button"
                    data-testid={`button-time-${slot.time.replaceAll(' ', '-')}`}
                    key={`${slot.time}-${slot.clinician}`}
                    className={cn('time-slot', time === slot.time && 'selected')}
                    onClick={() => setTime(slot.time)}
                  >
                    <span>{slot.time}</span>
                    <small>{slot.clinician}</small>
                    {time === slot.time && <Check size={14} />}
                  </button>
                ))
              ) : (
                <div className="inline-empty col-span-3">
                  No times found for this date. Try another day.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Step 3: Notes */}
        <div className="form-step">
          <span className="step-number">03</span>
          <div className="step-content">
            <label htmlFor="notes">Anything we should know?</label>
            <p>Optional notes for your care team.</p>
            <textarea
              id="notes"
              data-testid="textarea-notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Share anything that might help us prepare…"
              rows={4}
              maxLength={2000}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="booking-footer">
          <span>
            {time
              ? `${formatDate(date, { weekday: 'short', month: 'short', day: 'numeric' })} · ${time}`
              : 'Select a time to continue'}
          </span>
          <LoadingButton
            type="submit"
            loading={isSubmitting}
            disabled={!service || !time}
          >
            {isSubmitting ? 'Booking…' : 'Confirm appointment'}
          </LoadingButton>
        </div>
      </div>

      {/* Aside */}
      <aside className="booking-aside">
        <div className="booking-aside-art">
          <Heart size={35} fill="currentColor" />
        </div>
        <h3>A little preparation goes a long way.</h3>
        <p>
          After booking, you will see your clinician, location, and any notes
          you shared in one easy place.
        </p>
        <div className="aside-rule" />
        <div className="aside-detail">
          <ShieldCheck size={16} />
          Your appointment details stay private
        </div>
      </aside>
    </form>
  );
}