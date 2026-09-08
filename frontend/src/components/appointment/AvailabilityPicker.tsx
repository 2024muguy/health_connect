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
  const availableSlots = availability.filter((slot) => slot.available);

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
      {availableSlots.map((slot) => {
        const slotKey = `${slot.time}-${slot.clinician}`;
        const isSelected = selectedTime === slot.time;

        return (
          <button
            type="button"
            data-testid={`button-time-${slot.time.replaceAll(' ', '-')}`}
            key={slotKey}
            className={cn('time-slot', isSelected && 'selected')}
            onClick={() => onTimeSelect(slot.time)}
          >
            <span>{slot.time}</span>
            <small>{slot.clinician}</small>
            {isSelected && <Check size={14} />}
          </button>
        );
      })}
    </div>
  );
}