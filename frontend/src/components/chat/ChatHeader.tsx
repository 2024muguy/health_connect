/**
 * HealthConnect AI - ChatHeader Component
 * Chat conversation header
 */

'use client';

import { Sparkles, MoreVertical, Trash2 } from 'lucide-react';
import { Dropdown } from '@/components/ui/dropdown';
import { Avatar } from '@/components/ui/avatar';
import type { WebSocketStatus } from '@/lib/websocket';
import { cn } from '@/lib/utils';

interface ChatHeaderProps {
  conversationId?: string;
  patientName?: string;
  connectionStatus?: WebSocketStatus;
  onDelete?: () => void;
  className?: string;
}

export function ChatHeader({
  conversationId,
  patientName,
  connectionStatus = 'disconnected',
  onDelete,
  className,
}: ChatHeaderProps) {
  const statusLabel = {
    connecting: 'Connecting…',
    connected: 'Online',
    disconnected: 'Offline',
    reconnecting: 'Reconnecting…',
    error: 'Connection issue',
  }[connectionStatus];

  const statusColor = {
    connecting: 'bg-yellow-500',
    connected: 'bg-green-500',
    disconnected: 'bg-gray-400',
    reconnecting: 'bg-yellow-500',
    error: 'bg-destructive',
  }[connectionStatus];

  const dropdownItems = [
    {
      id: 'delete',
      label: 'Delete conversation',
      icon: <Trash2 size={14} />,
      danger: true,
      onClick: onDelete,
    },
  ];

  return (
    <div
      className={cn(
        'flex items-center justify-between px-5 py-4 border-b border-border bg-card',
        className,
      )}
    >
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-[12px] bg-primary/10 grid place-items-center">
          <Sparkles size={18} className="text-primary" />
        </div>
        <div>
          <h2 className="text-sm font-bold text-foreground">
            {patientName ? `Chat with ${patientName}` : 'Care Assistant'}
          </h2>
          <div className="flex items-center gap-1.5 mt-0.5">
            <span className={cn('w-1.5 h-1.5 rounded-full', statusColor)} />
            <span className="text-[10px] text-muted-foreground">{statusLabel}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Avatar initials="AI" small />
        {onDelete && (
          <Dropdown
            trigger={
              <button className="icon-button subtle" aria-label="More options">
                <MoreVertical size={17} />
              </button>
            }
            items={dropdownItems}
            align="right"
          />
        )}
      </div>
    </div>
  );
}