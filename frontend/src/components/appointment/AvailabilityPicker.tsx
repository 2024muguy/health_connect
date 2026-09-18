/**
 * HealthConnect AI - AvailabilityPicker Component
 * Time slot availability picker
 */

'use client';

import { Check, Clock3 } from 'lucide-react';
import type { AppointmentAvailability } from '@/types';
import { cn } from '@/lib/utils';
import { SkeletonBlock } from '@/components/ui/spinner';

interface AvailabilityPickerProps {
  availability: AppointmentAvailability[];
  selectedTime?: string;
  onTimeSelect: (time: string) => void;
  isLoading?: boolean;
  className?: string;
}

export function AvailabilityPicker({
  availability,
  selectedTime,
  onTimeSelect,
  isLoading = false,
  className,
}: AvailabilityPickerProps) {
  const slotsArray = Array.isArray(availability)
    ? availability
    : (availability as any)?.available_slots
      ?? (availability as any)?.availability
      ?? (availability as any)?.slots
      ?? [];

  const availableSlots = slotsArray.filter(
    (slot: AppointmentAvailability) => slot.available,
  );

  if (isLoading) {
    return (
      <div className={cn('grid grid-cols-3 gap-2', className)}>
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonBlock key={i} className="h-11" />
        ))}
      </div>
    );
  }

  if (availableSlots.length === 0) {
    return (
      <div className={cn('inline-empty', className)}>
        <Clock3 size={15} />
        No available times for the selected date.
      </div>
    );
  }

  return (
    <div className={cn('time-grid', className)}>
      {availableSlots.map((slot: AppointmentAvailability, idx: number) => {
        const slotKey = `${slot.time}-${slot.doctor_id ?? 'any'}-${idx}`;
        const isSelected = selectedTime === slot.time;
        const clinicianLabel = slot.clinician || 'Any clinician';

        return (
          <button
            type="button"
            data-testid={`button-time-${slot.time.replaceAll(' ', '-').replaceAll(':', '-')}`}
            key={slotKey}
            className={cn('time-slot', isSelected && 'selected')}
            onClick={() => onTimeSelect(slot.time)}
          >
            <span>{slot.time}</span>
            <small>{clinicianLabel}</small>
            {isSelected && <Check size={14} />}
          </button>
        );
      })}
    </div>
  );
}