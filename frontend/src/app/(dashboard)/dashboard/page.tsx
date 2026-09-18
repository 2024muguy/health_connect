/**
 * HealthConnect AI - Dashboard Page
 * Compact, glance-able overview with links to detailed pages
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
  Stethoscope,
  Navigation,
  Gift,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useAppointments } from '@/hooks/useAppointments';
import { useChat } from '@/hooks/useChat';
import { UpcomingAppointments } from '@/components/dashboard/UpcomingAppointments';
import { RecentConversations } from '@/components/dashboard/RecentConversations';
import { ClinicPreview } from '@/components/dashboard/ClinicPreview';
import { MapPreview } from '@/components/dashboard/MapPreview';
import { PromoPreview } from '@/components/dashboard/PromoPreview';
import { Skeleton } from '@/components/ui/skeleton';

export default function DashboardPage() {
  const { user } = useAuth();
  const { upcomingAppointments, loadAppointments, isLoading: appointmentsLoading } = useAppointments();
  const { conversations, loadConversations } = useChat();
  const [isInitialLoading, setIsInitialLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      await Promise.all([loadAppointments('upcoming'), loadConversations()]);
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
        {/* ============================================================
            MAIN COLUMN
            ============================================================ */}
        <section className="dashboard-main">
          {/* Next Appointment */}
          <div className="section-heading">
            <h2>Your next appointment</h2>
            <Link href="/appointments" className="text-link">
              See all <ArrowRight size={14} />
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
            <Link href="/chat" className="text-link">
              View all <ArrowRight size={14} />
            </Link>
          </div>

          <RecentConversations
            conversations={conversations}
            isLoading={isInitialLoading}
            maxItems={2}
          />

          {/* Quick Access to Clinic, Map, Offers */}
          <div className="section-heading mt-8">
            <h2>Explore</h2>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <Link
              href="/clinic"
              className="panel p-4 hover:border-primary/40 transition-colors group"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Stethoscope size={18} className="text-primary" />
                </div>
                <ArrowRight
                  size={14}
                  className="text-muted-foreground group-hover:text-primary transition-colors"
                />
              </div>
              <h3 className="text-sm font-semibold">Clinic Info</h3>
              <p className="text-[11px] text-muted-foreground mt-1 line-clamp-2">
                Hours, services, and contact details
              </p>
            </Link>

            <Link
              href="/clinic#directions"
              scroll={true}
              className="panel p-4 hover:border-primary/40 transition-colors group"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Navigation size={18} className="text-primary" />
                </div>
                <ArrowRight
                  size={14}
                  className="text-muted-foreground group-hover:text-primary transition-colors"
                />
              </div>
              <h3 className="text-sm font-semibold">Directions</h3>
              <p className="text-[11px] text-muted-foreground mt-1 line-clamp-2">
                Navigate to Ongata Rongai
              </p>
            </Link>

            <Link
              href="/clinic#offers"
              scroll={true}
              className="panel p-4 hover:border-primary/40 transition-colors group"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Gift size={18} className="text-primary" />
                </div>
                <ArrowRight
                  size={14}
                  className="text-muted-foreground group-hover:text-primary transition-colors"
                />
              </div>
              <h3 className="text-sm font-semibold">Special Offers</h3>
              <p className="text-[11px] text-muted-foreground mt-1 line-clamp-2">
                Free screenings & promotions
              </p>
            </Link>
          </div>
        </section>

        {/* ============================================================
            RIGHT RAIL
            ============================================================ */}
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
            <Link href="/chat" className="button button-light">
              Start a conversation <ArrowRight size={15} />
            </Link>
          </div>

          {/* Stats Card */}
          <div className="stats-card">
            <div className="stats-label">Your care, this year</div>
            <div className="stats-row">
              <div>
                <strong>{upcomingAppointments.length}</strong>
                <span>Visits</span>
              </div>
              <div>
                <strong>{conversations.length}</strong>
                <span>Chats</span>
              </div>
              <div>
                <strong>0</strong>
                <span>Documents</span>
              </div>
            </div>
            <div className="stats-foot">
              <ShieldCheck size={14} />
              Your information is private and secure
            </div>
          </div>

          {/* Compact Clinic Preview */}
          <ClinicPreview />

          {/* Compact Map Preview */}
          <MapPreview />

          {/* Compact Promo Preview */}
          <PromoPreview />

          {/* Quick Links */}
          <div className="quick-links">
            <span className="stats-label">Quick access</span>
            <Link href="/appointments/new">
              <CalendarDays size={16} /> Book appointment <ArrowRight size={14} />
            </Link>
            <Link href="/chat">
              <MessageCircle size={16} /> Care assistant <ArrowRight size={14} />
            </Link>
            <Link href="/clinic">
              <MapPin size={16} /> Clinic info <ArrowRight size={14} />
            </Link>
            <Link href="/profile">
              <UserRound size={16} /> Profile <ArrowRight size={14} />
            </Link>
          </div>
        </aside>
      </div>
    </>
  );
}
