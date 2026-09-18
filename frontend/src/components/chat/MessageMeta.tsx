'use client';

import type { ChatMessage } from '@/types/chat';

interface MessageMetaProps {
  message: ChatMessage;
}

export function MessageMeta({ message }: MessageMetaProps) {
  if (message.role !== 'assistant') return null;

  const badges: Array<{ label: string; tone: string }> = [];

  if (message.bookingCompleted) {
    badges.push({ label: '✓ Booked', tone: 'bg-green-100 text-green-800' });
  }
  if (message.requiresHuman) {
    badges.push({ label: 'Human handoff', tone: 'bg-amber-100 text-amber-800' });
  }
  if (message.uncertaintyGated) {
    badges.push({ label: 'Low confidence', tone: 'bg-rose-100 text-rose-800' });
  }
  if (typeof message.confidence === 'number' && message.confidence < 0.75) {
    const pct = Math.round(message.confidence * 100);
    const tone = pct >= 50 ? 'bg-amber-50 text-amber-700' : 'bg-rose-50 text-rose-700';
    badges.push({ label: `Confidence ${pct}%`, tone });
  }

  if (badges.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5 mt-2">
      {badges.map((b) => (
        <span
          key={b.label}
          className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium ${b.tone}`}
        >
          {b.label}
        </span>
      ))}
    </div>
  );
}
