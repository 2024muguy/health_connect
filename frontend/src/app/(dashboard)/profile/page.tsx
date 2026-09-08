/**
 * HealthConnect AI - Profile Page
 * Patient profile management
 */

'use client';

import { useEffect, useState, type FormEvent } from 'react';
import Link from 'next/link';
import {
  ShieldCheck,
  ArrowRight,
  Check,
  Lock,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Avatar } from '@/components/ui/avatar';
import { LoadingButton } from '@/components/ui/button';
import { useToast } from '@/hooks/useToast';
import { getInitials, formatDate } from '@/lib/utils';

export default function ProfilePage() {
  const { user, refreshProfile } = useAuth();
  const { toast } = useToast();
  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    phone: '',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);

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
    setSaved(false);
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsSaving(true);

    try {
      // In production, this would call the update profile API
      await new Promise((resolve) => setTimeout(resolve, 500));
      await