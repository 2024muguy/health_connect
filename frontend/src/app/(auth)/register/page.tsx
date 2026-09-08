/**
 * HealthConnect AI - Register Page
 * New patient registration
 */

'use client';

import { useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  User,
  Phone,
  HeartPulse,
  ArrowRight,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { LoadingButton } from '@/components/ui/button';
import { Logo } from '@/components/shared/Logo';
import { useToast } from '@/hooks/useToast';
import { cn } from '@/lib/utils';

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error: authError, clearError } = useAuth();
  const { toast } = useToast();

  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const handleChange = (key: keyof typeof form, value: string) => {
    setForm((old) => ({ ...old, [key]: value }));
    setFormError(null);
    clearError();
  };

  const validateForm = (): string | null => {
    if (form.firstName.trim().length < 2) return 'First name must be at least 2 characters.';
    if (form.lastName.trim().length < 2) return 'Last name must be at least 2 characters.';
    if (!form.email.includes('@')) return 'Please enter a valid email address.';
    if (form.password.length < 8) return 'Password must be at least 8 characters.';
    if (!/[A-Z]/.test(form.password)) return 'Password must contain an uppercase letter.';
    if (!/[a-z]/.test(form.password)) return 'Password must contain a lowercase letter.';
    if (!/[0-9]/.test(form.password)) return 'Password must contain a number.';
    if (form.password !== form.confirmPassword) return 'Passwords do not match.';
    return null;
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setFormError(null);
    clearError();

    const validationError = validateForm();
    if (validationError) {
      setFormError(validationError);
      return;
    }

    try {
      await register({
        email: form.email.trim(),
        password: form.password,
        firstName: form.firstName.trim(),
        lastName: form.lastName.trim(),
        phone: form.phone.trim() || undefined,
      });
      toast('Account created successfully!', 'success');
      router.push('/dashboard');
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Registration failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-background">
      {/* Left Panel - Visual */}
      <div className="hidden md:flex md:w-[40%] bg-sidebar relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-56 h-56 rounded-full border border-sidebar-primary/30" />
          <div className="absolute bottom-20 right-10 w-72 h-72 rounded-full border border-sidebar-primary/20" />
        </div>
        <div className="relative z-10 flex flex-col justify-center p-12 text-sidebar-foreground">
          <div className="w-14 h-14 rounded-2xl bg-accent grid place-items-center mb-8">
            <HeartPulse size={28} className="text-accent-foreground" />
          </div>
          <h2 className="font-serif text-4xl leading-tight tracking-tight">
            Join HealthConnect
          </h2>
          <p className="mt-4 text-sm text-sidebar-foreground/70 max-w-sm leading-relaxed">
            Create your patient account to book appointments, chat with your
            care assistant, and manage your healthcare journey.
          </p>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-6 md:p-12 overflow-y-auto">
        <div className="w-full max-w-md py-8">
          <div className="mb-8">
            <Logo variant="landing" size="sm" />
          </div>

          <h1 className="text-2xl font-semibold text-foreground tracking-tight">
            Create your account
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            A few details to get you started.
          </p>

          {(formError || authError) && (
            <div className="mt-6 p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-xs">
              {formError || authError}
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                  First name
                </label>
                <div className="relative">
                  <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input
                    data-testid="input-first-name"
                    type="text"
                    value={form.firstName}
                    onChange={(e) => handleChange('firstName', e.target.value)}
                    placeholder="Jane"
                    className="w-full h-[43px] pl-10 pr-3 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none transition-all focus:border-primary focus:ring-[3px] focus:ring-primary/12"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                  Last name
                </label>
                <div className="relative">
                  <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input
                    data-testid="input-last-name"
                    type="text"
                    value={form.lastName}
                    onChange={(e) => handleChange('lastName', e.target.value)}
                    placeholder="Doe"
                    className="w-full h-[43px] pl-10 pr-3 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none transition-all focus:border-primary focus:ring-[3px] focus:ring-primary/12"
                    required
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                Email address
              </label>
              <div className="relative">
                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <input
                  data-testid="input-email"
                  type="email"
                  value={form.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  placeholder="you@example.com"
                  className="w-full h-[43px] pl-10 pr-3 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none transition-all focus:border-primary focus:ring-[3px] focus:ring-primary/12"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                Phone number (optional)
              </label>
              <div className="relative">
                <Phone size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <input
                  data-testid="input-phone"
                  type="tel"
                  value={form.phone}
                  onChange={(e) => handleChange('phone', e.target.value)}
                  placeholder="(555) 123-4567"
                  className="w-full h-[43px] pl-10 pr-3 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none transition-all focus:border-primary focus:ring-[3px] focus:ring-primary/12"
                />
              </div>
            </div>

            <div>
              <label className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                Password
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <input
                  data-testid="input-password"
                  type={showPassword ? 'text' : 'password'}
                  value={form.password}
                  onChange={(e) => handleChange('password', e.target.value)}
                  placeholder="Min. 8 characters"
                  className="w-full h-[43px] pl-10 pr-10 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none transition-all focus:border-primary focus:ring-[3px] focus:ring-primary/12"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div>
              <label className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                Confirm password
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <input
                  data-testid="input-confirm-password"
                  type={showPassword ? 'text' : 'password'}
                  value={form.confirmPassword}
                  onChange={(e) => handleChange('confirmPassword', e.target.value)}
                  placeholder="Repeat your password"
                  className="w-full h-[43px] pl-10 pr-3 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none transition-all focus:border-primary focus:ring-[3px] focus:ring-primary/12"
                  required
                />
              </div>
            </div>

            <LoadingButton type="submit" loading={isLoading} fullWidth className="h-[46px]">
              {isLoading ? 'Creating account…' : 'Create account'}
            </LoadingButton>
          </form>

          <p className="mt-6 text-center text-xs text-muted-foreground">
            Already have an account?{' '}
            <Link href="/login" className="font-semibold text-primary hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}