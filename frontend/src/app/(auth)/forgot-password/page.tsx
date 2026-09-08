/**
 * HealthConnect AI - Forgot Password Page
 */

'use client';

import { useState, type FormEvent } from 'react';
import Link from 'next/link';
import { Mail, ArrowLeft, Check } from 'lucide-react';
import { Logo } from '@/components/shared/Logo';
import { LoadingButton } from '@/components/ui/button';
import { useToast } from '@/hooks/useToast';

export default function ForgotPasswordPage() {
  const { toast } = useToast();
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);

    if (!email.trim() || !email.includes('@')) {
      setError('Please enter a valid email address.');
      return;
    }

    setIsSubmitting(true);
    try {
      // In production, this would call the password reset API
      await new Promise((resolve) => setTimeout(resolve, 800));
      setSubmitted(true);
      toast('Password reset link sent!', 'success');
    } catch {
      setError('Failed to send reset link. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-6">
      <div className="w-full max-w-md">
        <div className="mb-10">
          <Logo variant="landing" size="sm" />
        </div>

        {submitted ? (
          <div className="text-center">
            <div className="w-14 h-14 mx-auto mb-6 rounded-2xl bg-primary/10 grid place-items-center">
              <Check size={28} className="text-primary" />
            </div>
            <h1 className="text-2xl font-semibold text-foreground">
              Check your email
            </h1>
            <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
              We&apos;ve sent a password reset link to{' '}
              <span className="font-semibold text-foreground">{email}</span>.
              The link will expire in 30 minutes.
            </p>
            <Link
              href="/login"
              className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-primary hover:underline"
            >
              <ArrowLeft size={15} />
              Back to sign in
            </Link>
          </div>
        ) : (
          <>
            <h1 className="text-2xl font-semibold text-foreground tracking-tight">
              Reset your password
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Enter your email and we&apos;ll send you a reset link.
            </p>

            {error && (
              <div className="mt-6 p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-xs">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-8 space-y-5">
              <div>
                <label className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                  Email address
                </label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full h-[43px] pl-10 pr-3 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none transition-all focus:border-primary focus:ring-[3px] focus:ring-primary/12"
                    required
                  />
                </div>
              </div>

              <LoadingButton type="submit" loading={isSubmitting} fullWidth className="h-[46px]">
                {isSubmitting ? 'Sending…' : 'Send reset link'}
              </LoadingButton>
            </form>

            <p className="mt-6 text-center text-xs text-muted-foreground">
              Remember your password?{' '}
              <Link href="/login" className="font-semibold text-primary hover:underline">
                Sign in
              </Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}