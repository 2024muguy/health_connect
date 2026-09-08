/**
 * HealthConnect AI - Form Validators
 */

import { z } from 'zod';

// Email validator
export const emailSchema = z
  .string()
  .email('Please enter a valid email address')
  .min(5, 'Email is too short')
  .max(255, 'Email is too long');

// Password validator
export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .max(100, 'Password must be less than 100 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number');

// Name validator
export const nameSchema = z
  .string()
  .min(2, 'Must be at least 2 characters')
  .max(100, 'Must be less than 100 characters')
  .regex(/^[A-Za-z\s\-']+$/, 'Contains invalid characters');

// Phone validator
export const phoneSchema = z
  .string()
  .min(7, 'Phone number is too short')
  .max(20, 'Phone number is too long')
  .regex(/^[+]?[\d\s\-()]+$/, 'Invalid phone number format');

// Login schema
export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
});

// Register schema
export const registerSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  firstName: nameSchema,
  lastName: nameSchema,
  phone: phoneSchema.optional(),
});

// Profile update schema
export const profileUpdateSchema = z.object({
  firstName: nameSchema,
  lastName: nameSchema,
  phone: phoneSchema,
});

// Appointment booking schema
export const appointmentBookingSchema = z.object({
  service: z.string().min(1, 'Please select a service'),
  date: z.string().min(1, 'Please select a date'),
  time: z.string().min(1, 'Please select a time'),
  notes: z.string().max(2000, 'Notes must be less than 2000 characters').optional(),
});

// Chat message schema
export const chatMessageSchema = z.object({
  message: z
    .string()
    .min(1, 'Message cannot be empty')
    .max(2000, 'Message must be less than 2000 characters'),
  conversationId: z.string().optional(),
  sessionToken: z.string().optional(),
});

// Feedback schema
export const feedbackSchema = z.object({
  conversationId: z.string(),
  satisfactionScore: z.number().min(1).max(5),
  feedbackText: z.string().max(1000).optional(),
  helpful: z.boolean().optional(),
});

// Type exports
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ProfileUpdateData = z.infer<typeof profileUpdateSchema>;
export type AppointmentBookingData = z.infer<typeof appointmentBookingSchema>;
export type ChatMessageData = z.infer<typeof chatMessageSchema>;
export type FeedbackData = z.infer<typeof feedbackSchema>;