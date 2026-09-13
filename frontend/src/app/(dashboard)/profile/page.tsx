/**
 * HealthConnect AI - Profile Page
 * Patient profile management
 */

'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { LoadingButton } from '@/components/ui/button';
import { useToast } from '@/hooks/useToast';
import { getInitials } from '@/lib/utils';

export default function ProfilePage() {
  const { user, refreshProfile } = useAuth();
  const { toast } = useToast();
  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    phone: '',
  });
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setForm({
        firstName: user.firstName || '',
        lastName: user.lastName || '',
        phone: user.phone || '',
      });
    }
  }, [user]);

  const handleChange = (key: keyof typeof form, value: string) => {
    setForm((old) => ({ ...old, [key]: value }));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsSaving(true);

    try {
      // In production, this would call the update profile API
      await new Promise((resolve) => setTimeout(resolve, 500));
      await refreshProfile();
      toast('Profile updated successfully.', 'success');
    } catch {
      toast('Failed to update profile.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <p className="text-sm text-muted-foreground">Loading profile…</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <p className="eyebrow">Your account</p>
        <h1 className="page-title">Profile</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Manage your personal details and preferences.
        </p>
      </div>

      <div className="panel p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold">
            {getInitials(user.firstName || '', user.lastName || '')}
          </div>
          <div>
            <div className="font-semibold text-foreground">{user.full_name || 'User'}</div>
            <div className="text-xs text-muted-foreground">{user.email}</div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                First name
              </label>
              <input
                type="text"
                value={form.firstName}
                onChange={(e) => handleChange('firstName', e.target.value)}
                className="w-full h-[43px] px-3 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                Last name
              </label>
              <input
                type="text"
                value={form.lastName}
                onChange={(e) => handleChange('lastName', e.target.value)}
                className="w-full h-[43px] px-3 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label className="block mb-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
              Phone number
            </label>
            <input
              type="tel"
              value={form.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
              className="w-full h-[43px] px-3 rounded-[10px] border border-input bg-background text-xs text-foreground outline-none focus:border-primary"
            />
          </div>

          <LoadingButton type="submit" loading={isSaving} fullWidth className="h-[46px]">
            {isSaving ? 'Saving…' : 'Save changes'}
          </LoadingButton>
        </form>
      </div>
    </div>
  );
}
