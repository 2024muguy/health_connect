/**
 * HealthConnect AI - Admin Escalations Page
 */

'use client';

import { useState } from 'react';
import {
  MessageCircle,
  AlertTriangle,
  Check,
  Clock3,
  Filter,
} from 'lucide-react';
import { Tabs } from '@/components/ui/tabs';
import { EmptyState } from '@/components/shared/EmptyState';
import { Badge } from '@/components/ui/badge';
import { formatRelative } from '@/lib/utils';

interface Escalation {
  id: string;
  code: string;
  type: string;
  priority: 'low' | 'normal' | 'high' | 'critical';
  status: 'pending' | 'assigned' | 'resolved';
  reason: string;
  createdAt: string;
  department: string;
}

export default function AdminEscalationsPage() {
  const [activeTab, setActiveTab] = useState('pending');
  const [escalations] = useState<Escalation[]>([]);

  const tabs = [
    { id: 'pending', label: 'Pending', count: escalations.filter(e => e.status === 'pending').length },
    { id: 'assigned', label: 'Assigned', count: escalations.filter(e => e.status === 'assigned').length },
    { id: 'resolved', label: 'Resolved', count: escalations.filter(e => e.status === 'resolved').length },
  ];

  const filteredEscalations = escalations.filter((e) => e.status === activeTab);

  return (
    <>
      <div className="mb-8">
        <p className="eyebrow">Administration</p>
        <h1 className="page-title">Escalations</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Track and manage patient escalations.
        </p>
      </div>

      <div className="filter-bar">
        <Tabs
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={setActiveTab}
          variant="segmented"
        />
        <button className="icon-button subtle">
          <Filter size={16} />
        </button>
      </div>

      {filteredEscalations.length === 0 ? (
        <EmptyState
          icon={MessageCircle}
          title={`No ${activeTab} escalations`}
          text="Escalations from patient conversations will appear here."
        />
      ) : (
        <div className="space-y-3">
          {filteredEscalations.map((escalation) => (
            <div
              key={escalation.id}
              className="rounded-[17px] border border-card-border bg-card p-5"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-[10px] grid place-items-center ${
                    escalation.priority === 'critical' ? 'bg-destructive/10 text-destructive' :
                    escalation.priority === 'high' ? 'bg-accent/18 text-[hsl(32_66%_37%)]' :
                    'bg-primary/10 text-primary'
                  }`}>
                    <AlertTriangle size={15} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-foreground">{escalation.code}</span>
                      <Badge variant={escalation.priority === 'critical' ? 'danger' : escalation.priority === 'high' ? 'warning' : 'primary'}>
                        {escalation.priority}
                      </Badge>
                    </div>
                    <p className="text-[11px] text-muted-foreground mt-1">{escalation.reason}</p>
                    <p className="text-[10px] text-muted-foreground/60 mt-1">
                      {escalation.department} · {formatRelative(escalation.createdAt)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {escalation.status === 'pending' && (
                    <button className="button button-primary text-[10px] px-3 py-1.5 min-h-0">
                      Assign
                    </button>
                  )}
                  {escalation.status === 'assigned' && (
                    <button className="button button-secondary text-[10px] px-3 py-1.5 min-h-0">
                      <Check size={12} />
                      Resolve
                    </button>
                  )}
                  {escalation.status === 'resolved' && (
                    <span className="inline-flex items-center gap-1 text-[10px] text-primary">
                      <Clock3 size={12} />
                      Resolved
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}