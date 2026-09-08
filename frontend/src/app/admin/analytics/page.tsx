/**
 * HealthConnect AI - Admin Analytics Page
 */

'use client';

import { useState } from 'react';
import {
  BarChart3,
  Download,
  CalendarDays,
  MessageCircle,
  Activity,
} from 'lucide-react';
import { StatCard } from '@/components/dashboard/StatCard';
import { ActivityChart } from '@/components/dashboard/ActivityChart';
import { Tabs } from '@/components/ui/tabs';
import { EmptyState } from '@/components/shared/EmptyState';

export default function AdminAnalyticsPage() {
  const [period, setPeriod] = useState('daily');

  const tabs = [
    { id: 'daily', label: 'Daily' },
    { id: 'weekly', label: 'Weekly' },
    { id: 'monthly', label: 'Monthly' },
  ];

  const activityData = [
    { label: 'Mon', value: 12 },
    { label: 'Tue', value: 18 },
    { label: 'Wed', value: 15 },
    { label: 'Thu', value: 22 },
    { label: 'Fri', value: 28 },
    { label: 'Sat', value: 8 },
    { label: 'Sun', value: 5 },
  ];

  return (
    <>
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
        <div>
          <p className="eyebrow">System analytics</p>
          <h1 className="page-title">Analytics</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Performance metrics and usage trends.
          </p>
        </div>
        <button className="button button-secondary">
          <Download size={15} />
          Export report
        </button>
      </div>

      <div className="filter-bar mb-6">
        <Tabs tabs={tabs} activeTab={period} onTabChange={setPeriod} variant="segmented" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <StatCard label="Total conversations" value={128} icon={MessageCircle} trend={15} />
        <StatCard label="Appointments" value={342} icon={CalendarDays} trend={8} />
        <StatCard label="Avg response time" value="850ms" icon={Activity} variant="accent" />
      </div>

      <div className="rounded-[17px] border border-card-border bg-card p-6">
        <div className="section-heading">
          <h2>Weekly activity</h2>
          <span className="muted-count">Conversations per day</span>
        </div>
        <ActivityChart data={activityData} height={200} />
      </div>
    </>
  );
}