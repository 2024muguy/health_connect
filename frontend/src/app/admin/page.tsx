/**
 * HealthConnect AI - Admin Dashboard Page
 */

'use client';

import { useEffect, useState } from 'react';
import {
  Users,
  CalendarDays,
  MessageCircle,
  AlertTriangle,
  TrendingUp,
  Activity,
} from 'lucide-react';
import { StatCard } from '@/components/dashboard/StatCard';
import { ActivityChart } from '@/components/dashboard/ActivityChart';
import { Skeleton } from '@/components/ui/skeleton';
import { analyticsApi } from '@/lib/api';
import type { AnalyticsMetrics } from '@/types';

export default function AdminDashboardPage() {
  const [metrics, setMetrics] = useState<AnalyticsMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        const data = await analyticsApi.getMetrics();
        setMetrics(data);
      } catch {
        // Handle error
      } finally {
        setIsLoading(false);
      }
    };
    loadMetrics();
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-[120px] w-full" variant="card" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-[100px]" variant="card" />
          ))}
        </div>
      </div>
    );
  }

  const hourlyData = metrics?.hourly_activity
    ? Object.entries(metrics.hourly_activity).map(([hour, count]) => ({
        label: hour,
        value: count,
      }))
    : [];

  return (
    <>
      <div className="mb-8">
        <p className="eyebrow">System overview</p>
        <h1 className="page-title">Admin dashboard</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Total conversations"
          value={metrics?.total_conversations || 0}
          icon={MessageCircle}
          trend={12}
          trendLabel="vs last week"
        />
        <StatCard
          label="Total appointments"
          value={metrics?.total_appointments || 0}
          icon={CalendarDays}
          trend={5}
          trendLabel="vs last week"
        />
        <StatCard
          label="Escalations"
          value={metrics?.total_escalations || 0}
          icon={AlertTriangle}
          trend={-8}
          trendLabel="vs last week"
        />
        <StatCard
          label="No-show rate"
          value={`${(metrics?.no_show_rate || 0).toFixed(1)}%`}
          icon={Activity}
          variant="accent"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Chart */}
        <div className="rounded-[17px] border border-card-border bg-card p-6">
          <div className="section-heading">
            <h2>Hourly activity</h2>
            <span className="muted-count">Last 24 hours</span>
          </div>
          <ActivityChart data={hourlyData} height={180} />
        </div>

        {/* Top Intents */}
        <div className="rounded-[17px] border border-card-border bg-card p-6">
          <div className="section-heading">
            <h2>Top intents</h2>
            <TrendingUp size={16} className="text-primary" />
          </div>
          {metrics?.top_intents && Object.entries(metrics.top_intents).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(metrics.top_intents).slice(0, 5).map(([intent, count], index) => (
                <div key={intent} className="flex items-center gap-3">
                  <span className="text-[10px] font-mono text-muted-foreground w-5">
                    {String(index + 1).padStart(2, '0')}
                  </span>
                  <div className="flex-1">
                    <div className="flex justify-between mb-1">
                      <span className="text-xs font-medium text-foreground">{intent}</span>
                      <span className="text-[10px] text-muted-foreground">{count}</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full rounded-full bg-primary"
                        style={{ width: `${Math.min(100, (count / Math.max(...Object.values(metrics.top_intents))) * 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">No intent data available yet.</p>
          )}
        </div>
      </div>
    </>
  );
}