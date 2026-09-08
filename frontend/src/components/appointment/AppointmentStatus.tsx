/**
 * HealthConnect AI - AppointmentStatus Component
 * Appointment status indicator with timeline
 */

'use client';

import { Check, Clock3, X, CalendarClock, AlertTriangle } from 'lucide-react';
import type { AppointmentStatus as Status } from '@/types';
import { cn } from '@/lib/utils';

interface AppointmentStatusProps {
  status: Status;
  className?: string;
}

const statusConfig: Record<Status, {
  label: string;
  icon: typeof Check;
  color: string;
  bgColor: string;
  description: string;
}> = {
  scheduled: {
    label: 'Scheduled',
    icon: CalendarClock,
    color: 'text-primary',
    bgColor: 'bg-primary/10',
    description: 'Your appointment is scheduled',
  },
  confirmed: {
    label: 'Confirmed',
    icon: Check,
    color: 'text-[hsl(166_40%_29%)]',
    bgColor: 'bg-primary/14',
    description: 'Your appointment is confirmed',
  },
  checked_in: {
    label: 'Checked In',
    icon: Check,
    color: 'text-primary',
    bgColor: 'bg-primary/14',
    description: 'You have checked in',
  },
  in_progress: {
    label: 'In Progress',
    icon: Clock3,
    color: 'text-[hsl(32_66%_37%)]',
    bgColor: 'bg-accent/18',
    description: 'Your appointment is in progress',
  },
  completed: {
    label: 'Completed',
    icon: Check,
    color: 'text-muted-foreground',
    bgColor: 'bg-muted',
    description: 'This appointment has been completed',
  },
  cancelled: {
    label: 'Cancelled',
    icon: X,
    color: 'text-destructive',
    bgColor: 'bg-destructive/10',
    description: 'This appointment was cancelled',
  },
  no_show: {
    label: 'No Show',
    icon: AlertTriangle,
    color: 'text-destructive',
    bgColor: 'bg-destructive/10',
    description: 'This appointment was missed',
  },
  rescheduled: {
    label: 'Rescheduled',
    icon: CalendarClock,
    color: 'text-[hsl(32_66%_37%)]',
    bgColor: 'bg-accent/18',
    description: 'This appointment was rescheduled',
  },
  pending: {
    label: 'Pending',
    icon: Clock3,
    color: 'text-[hsl(32_66%_37%)]',
    bgColor: 'bg-accent/18',
    description: 'Awaiting confirmation',
  },
};

export function AppointmentStatus({ status, className }: AppointmentStatusProps) {
  const config = statusConfig[status] || statusConfig.pending;
  const Icon = config.icon;

  const steps: Status[] = ['scheduled', 'confirmed', 'checked_in', 'in_progress', 'completed'];
  const currentStepIndex = steps.indexOf(status);
  const isNegativeStatus = status === 'cancelled' || status === 'no_show';
  const isRescheduled = status === 'rescheduled';

  return (
    <div className={cn('space-y-4', className)}>
      {/* Current status badge */}
      <div className={cn('inline-flex items-center gap-2.5 px-3.5 py-2 rounded-xl', config.bgColor)}>
        <Icon size={16} className={config.color} />
        <div>
          <span className={cn('block text-xs font-bold', config.color)}>{config.label}</span>
          <span className="block text-[10px] text-muted-foreground">{config.description}</span>
        </div>
      </div>

      {/* Timeline */}
      {!isNegativeStatus && !isRescheduled && (
        <div className="flex items-center gap-1">
          {steps.map((step, index) => {
            const StepIcon = statusConfig[step].icon;
            const isComplete = index < currentStepIndex;
            const isCurrent = index === currentStepIndex;
            const isUpcoming = index > currentStepIndex;

            return (
              <div key={step} className="flex items-center flex-1">
                {/* Connector */}
                {index > 0 && (
                  <div
                    className={cn(
                      'flex-1 h-0.5 mx-1 rounded-full',
                      isComplete ? 'bg-primary' : 'bg-muted',
                    )}
                  />
                )}
                <div
                  className={cn(
                    'w-7 h-7 rounded-full grid place-items-center transition-all',
                    isComplete && 'bg-primary text-primary-foreground',
                    isCurrent && 'bg-primary/20 text-primary ring-2 ring-primary',
                    isUpcoming && 'bg-muted text-muted-foreground',
                  )}
                >
                  <StepIcon size={13} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}