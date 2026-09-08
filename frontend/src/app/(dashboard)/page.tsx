/**
 * HealthConnect AI - Dashboard Page
 * Main dashboard overview
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Heart,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  CalendarDays,
  MessageCircle,
  MapPin,
  UserRound,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useAppointments } from '@/hooks/useAppointments';
import { useChat } from '@/hooks/useChat';
import { StatCard } from '@/components/dashboard/StatCard';
import { UpcomingAppointments } from '@/components/dashboard/UpcomingAppointments';
import { RecentConversations } from '@/components/dashboard/RecentConversations';
import { EmptyState } from '@/components/shared/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDate } from '@/lib/utils';

export default function DashboardPage() {
  const { user } = useAuth();
  const { upcomingAppointments, loadAppointments, isLoading: appointmentsLoading } = useAppointments();
  const { conversations, loadConversations, isLoading: conversationsLoading } = useChat();
  const [isInitialLoading, setIsInitialLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      await Promise.all([
        loadAppointments('upcoming'),
        loadConversations(),
      ]);
      setIsInitialLoading(false);
    };
    loadData();
  }, [loadAppointments, loadConversations]);

  const firstName = user?.firstName || 'there';
  const today = new Date();

  return (
    <>
      {/* Welcome Row */}
      <div className="welcome-row">
        <div>
          <p className="eyebrow">
            {today.toLocaleDateString('en-US', {
              weekday: 'long',
              month: 'long',
              day: 'numeric',
              year: 'numeric',
            })}
          </p>
          <h1 className="page-title">
            Good morning, <em>{firstName}</em>
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Your care, thoughtfully organized.
          </p>
        </div>
        <div className="welcome-mark">
          <Heart size={25} fill="currentColor" />
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Main Column */}
        <section className="dashboard-main">
          {/* Next Appointment */}
          <div className="section-heading">
            <h2>Your next appointment</h2>
            <Link
              href="/appointments"
              className="text-link"
              data-testid="link-see-all-appointments"
            >
              See all
              <ArrowRight size={14} />
            </Link>
          </div>

          {appointmentsLoading ? (
            <Skeleton className="h-[80px] w-full" variant="card" />
          ) : (
            <UpcomingAppointments
              appointments={upcomingAppointments}
              isLoading={appointmentsLoading}
              maxItems={1}
            />
          )}

          {/* Recent Conversations */}
          <div className="section-heading mt-8">
            <h2>Recent conversations</h2>
            <Link
              href="/chat"
              className="text-link"
              data-testid="link-view-conversations"
            >
              View conversations
              <ArrowRight size={14} />
            </Link>
          </div>

          <RecentConversations
            conversations={conversations}
            isLoading={conversationsLoading}
            maxItems={3}
          />
        </section>

        {/* Right Rail */}
        <aside className="dashboard-rail">
          {/* Assistant Card */}
          <div className="assistant-card">
            <div className="assistant-card-top">
              <div className="assistant-spark">
                <Sparkles size={18} />
              </div>
              <span className="micro-label light">CARE ASSISTANT</span>
            </div>
            <h2>Small questions are welcome.</h2>
            <p>
              Get clear answers about your care, anytime. Your assistant
              remembers the context so you do not have to repeat yourself.
            </p>
            <Link
              href="/chat"
              className="button button-light"
              data-testid="link-start-conversation"
            >
              Start a conversation
              <ArrowRight size={15} />
            </Link>
          </div>

          {/* Stats Card */}
          <div className="stats-card">
            <div className="stats-label">Your care, this year</div>
            <div className="stats-row">
              <div>
                <strong data-testid="text-stat-visits">
                  {upcomingAppointments.length}
                </strong>
                <span>Visits</span>
              </div>
              <div>
                <strong data-testid="text-stat-care-team">0</strong>
                <span>Care team</span>
              </div>
              <div>
                <strong data-testid="text-stat-documents">0</strong>
                <span>Documents</span>
              </div>
            </div>
            <div className="stats-foot">
              <ShieldCheck size={14} />
              Your information is private and secure
            </div>
          </div>

          {/* Quick Links */}
          <div className="quick-links">
            <span className="stats-label">Quick access</span>
            <Link href="/clinic" data-testid="link-clinic-quick">
              <MapPin size={16} />
              Clinic information
              <ArrowRight size={14} />
            </Link>
            <Link href="/appointments/new" data-testid="link-book-quick">
              <CalendarDays size={16} />
              Book appointment
              <ArrowRight size={14} />
            </Link>
            <Link href="/profile" data-testid="link-profile-quick">
              <UserRound size={16} />
              Profile & preferences
              <ArrowRight size={14} />
            </Link>
          </div>
        </aside>
      </div>
    </>
  );
}