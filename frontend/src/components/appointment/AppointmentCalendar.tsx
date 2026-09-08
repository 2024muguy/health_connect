/**
 * HealthConnect AI - AppointmentCalendar Component
 * Monthly calendar view for appointments
 */

'use client';

import { useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import type { Appointment } from '@/types';
import { cn, formatDate } from '@/lib/utils';

interface AppointmentCalendarProps {
  appointments: Appointment[];
  onDateSelect?: (date: string) => void;
  selectedDate?: string;
  className?: string;
}

export function AppointmentCalendar({
  appointments,
  onDateSelect,
  selectedDate,
  className,
}: AppointmentCalendarProps) {
  const [currentMonth, setCurrentMonth] = useState(() => new Date());

  const daysInMonth = useMemo(() => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    return new Date(year, month + 1, 0).getDate();
  }, [currentMonth]);

  const firstDayOfMonth = useMemo(() => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    return new Date(year, month, 1).getDay();
  }, [currentMonth]);

  const appointmentsByDate = useMemo(() => {
    const map = new Map<string, Appointment[]>();
    appointments.forEach((appointment) => {
      const dateKey = appointment.date;
      if (!map.has(dateKey)) map.set(dateKey, []);
      map.get(dateKey)!.push(appointment);
    });
    return map;
  }, [appointments]);

  const monthLabel = currentMonth.toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric',
  });

  const handlePrevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const getDateKey = (day: number): string => {
    const year = currentMonth.getFullYear();
    const month = String(currentMonth.getMonth() + 1).padStart(2, '0');
    const dayStr = String(day).padStart(2, '0');
    return `${year}-${month}-${dayStr}`;
  };

  const weekdayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className={cn('rounded-[17px] border border-card-border bg-card p-5', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-foreground">{monthLabel}</h3>
        <div className="flex gap-1">
          <button
            onClick={handlePrevMonth}
            className="icon-button subtle"
            aria-label="Previous month"
          >
            <ChevronLeft size={16} />
          </button>
          <button
            onClick={handleNextMonth}
            className="icon-button subtle"
            aria-label="Next month"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Weekday labels */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {weekdayLabels.map((day) => (
          <div
            key={day}
            className="text-center text-[9px] font-mono uppercase tracking-wider text-muted-foreground"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-1">
        {/* Empty cells for days before start of month */}
        {Array.from({ length: firstDayOfMonth }).map((_, i) => (
          <div key={`empty-${i}`} className="h-[38px]" />
        ))}

        {/* Day cells */}
        {Array.from({ length: daysInMonth }).map((_, i) => {
          const day = i + 1;
          const dateKey = getDateKey(day);
          const hasAppointments = appointmentsByDate.has(dateKey);
          const appointmentCount = appointmentsByDate.get(dateKey)?.length || 0;
          const isSelected = selectedDate === dateKey;
          const isToday = dateKey === new Date().toISOString().slice(0, 10);

          return (
            <button
              key={dateKey}
              onClick={() => onDateSelect?.(dateKey)}
              className={cn(
                'relative h-[38px] rounded-[9px] text-xs font-medium transition-all flex flex-col items-center justify-center',
                hasAppointments
                  ? 'bg-primary/10 text-primary hover:bg-primary/20'
                  : 'text-foreground hover:bg-muted',
                isSelected && 'ring-2 ring-primary',
                isToday && 'font-bold underline',
              )}
            >
              {day}
              {appointmentCount > 0 && (
                <span className="absolute bottom-1 w-1 h-1 rounded-full bg-primary" />
              )}
            </button>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-4 pt-3 border-t border-border">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-primary/20" />
          <span className="text-[10px] text-muted-foreground">Has appointments</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-primary" />
          <span className="text-[10px] text-muted-foreground">Selected</span>
        </div>
      </div>
    </div>
  );
}