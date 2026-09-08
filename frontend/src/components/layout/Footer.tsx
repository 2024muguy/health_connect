/**
 * HealthConnect AI - Footer Component
 */

'use client';

import Link from 'next/link';
import { HeartPulse, ShieldCheck } from 'lucide-react';
import { APP_NAME, APP_VERSION } from '@/lib/constants';

interface FooterProps {
  className?: string;
}

export function Footer({ className }: FooterProps) {
  return (
    <footer className={`border-t border-border bg-card/50 ${className || ''}`}>
      <div className="max-w-[1260px] mx-auto px-6 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Brand */}
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-primary grid place-items-center">
              <HeartPulse size={15} className="text-primary-foreground" />
            </div>
            <div>
              <span className="text-xs font-bold text-foreground">{APP_NAME}</span>
              <span className="ml-2 text-[9px] font-mono text-muted-foreground">
                v{APP_VERSION}
              </span>
            </div>
          </div>

          {/* Links */}
          <nav className="flex flex-wrap items-center gap-6">
            <Link
              href="/clinic"
              className="text-[11px] text-muted-foreground hover:text-primary transition-colors"
            >
              Clinic information
            </Link>
            <Link
              href="/profile"
              className="text-[11px] text-muted-foreground hover:text-primary transition-colors"
            >
              My profile
            </Link>
            <Link
              href="/chat"
              className="text-[11px] text-muted-foreground hover:text-primary transition-colors"
            >
              Care assistant
            </Link>
          </nav>

          {/* Security note */}
          <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
            <ShieldCheck size={14} className="text-primary" />
            Your information is private and secure
          </div>
        </div>

        <div className="mt-6 pt-5 border-t border-border text-center">
          <p className="text-[9px] font-mono text-muted-foreground/60 uppercase tracking-wider">
            HealthConnect AI · For administrative support only · Not for medical emergencies
          </p>
        </div>
      </div>
    </footer>
  );
}