/**
 * HealthConnect AI - Login Page
 * Patient authentication
 */

'use client';

import { useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Mail, Lock, Eye, EyeOff, HeartPulse, ArrowRight } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { LoadingButton } from '@/components/ui/button';
import { Logo } from '@/components/shared/Logo';
import { useToast } from '@/hooks/useToast';
import { cn } from '@/lib/utils';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error: authError, clearError } = useAuth();
  const { toast } = useToast();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setFormError(null);
    clearError();

    // Basic validation
    if (!email.trim()) {
      setFormError('Please enter your email address.');
      return;
    }
    if (!password) {
      setFormError('Please enter your password.');
      return;
    }

    setSubmitting(true);
    try {
      await login({ email: email.trim(), password });
      toast('Welcome back!', 'success');
      router.push('/dashboard');
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Login failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-background">
      {/* Left Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-6 md:p-12">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="mb-10">
            <Logo variant="landing" size="md" />
          </div>

          <h1 className="text-3xl font-semibold text-foreground tracking-tight">
            Welcome back
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Sign in to manage your care and appointments.
          </p>

          {/* Error Alert */}
          {(formError || authError) && (
            <div className="mt-6 p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-xs">
              {formError || authError}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div>
              <label
                htmlFor="email"
                className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground"
              >
                Email address
              </label>
              <div className="relative">
                <Mail
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                />
                <input
                  id="email"
                  data-testid="input-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full h-[43px] pl-10 pr-3 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none transition-all focus:border-primary focus:ring-[3px] focus:ring-primary/12"
                  autoComplete="email"
                  required
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground"
              >
                Password
              </label>
              <div className="relative">
                <Lock
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                />
                <input
                  id="password"
                  data-testid="input-password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full h-[43px] pl-10 pr-10 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none transition-all focus:border-primary focus:ring-[3px] focus:ring-primary/12"
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-border text-primary focus:ring-primary"
                />
                <span className="text-xs text-muted-foreground">Remember me</span>
              </label>
              <Link
                href="/forgot-password"
                className="text-xs font-semibold text-primary hover:underline"
              >
                Forgot password?
              </Link>
            </div>

            <LoadingButton
              type="submit"
              loading={submitting}
              fullWidth
              className="h-[46px]"
            >
              {submitting ? 'Signing in…' : 'Sign in'}
            </LoadingButton>
          </form>

          <p className="mt-6 text-center text-xs text-muted-foreground">
            Don&apos;t have an account?{' '}
            <Link
              href="/register"
              className="font-semibold text-primary hover:underline"
            >
              Create one
            </Link>
          </p>
        </div>
      </div>

      {/* Right Panel - Visual */}
      <div className="hidden md:flex md:w-[45%] bg-sidebar relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 right-10 w-64 h-64 rounded-full border border-sidebar-primary/30" />
          <div className="absolute bottom-20 left-10 w-80 h-80 rounded-full border border-sidebar-primary/20" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full border border-sidebar-primary/15" />
        </div>
        <div className="relative z-10 flex flex-col justify-center p-12 text-sidebar-foreground">
          <div className="w-14 h-14 rounded-2xl bg-sidebar-primary grid place-items-center mb-8">
            <HeartPulse size={28} className="text-sidebar-primary-foreground" />
          </div>
          <h2 className="font-serif text-4xl leading-tight tracking-tight">
            Your care,<br />thoughtfully organized.
          </h2>
          <p className="mt-4 text-sm text-sidebar-foreground/70 max-w-sm leading-relaxed">
            Manage appointments, chat with your care assistant, and access
            clinic information all in one calm, secure place.
          </p>
          <div className="mt-8 flex items-center gap-2 text-sidebar-foreground/60 text-xs">
            <span className="w-2 h-2 rounded-full bg-sidebar-primary" />
            Care network online
          </div>
        </div>
      </div>
    </div>
  );
}