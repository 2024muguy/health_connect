/**
 * HealthConnect AI - Billing Page
 * Patient billing and payment information
 */

'use client';

import { useState } from 'react';
import {
  CreditCard,
  FileText,
  Download,
  CheckCircle2,
  Clock3,
  AlertCircle,
  ShieldCheck,
  ArrowRight,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/shared/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDate, cn } from '@/lib/utils';

interface Invoice {
  id: string;
  invoiceNumber: string;
  date: string;
  amount: number;
  status: 'paid' | 'pending' | 'overdue';
  description: string;
}

interface PaymentMethod {
  id: string;
  type: 'card' | 'bank';
  last4: string;
  expiry?: string;
  isDefault: boolean;
}

export default function BillingPage() {
  const [isLoading] = useState(false);
  const [invoices] = useState<Invoice[]>([]);
  const [paymentMethods] = useState<PaymentMethod[]>([]);

  const totalOutstanding = invoices
    .filter((inv) => inv.status !== 'paid')
    .reduce((sum, inv) => sum + inv.amount, 0);

  return (
    <>
      <div className="mb-8">
        <p className="eyebrow">Payments & insurance</p>
        <h1 className="page-title">Billing</h1>
        <p className="mt-2 text-sm text-muted-foreground max-w-xl">
          View your invoices, payment methods, and insurance information.
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="rounded-[17px] border border-card-border bg-card p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[9px] font-mono uppercase tracking-[0.1em] text-muted-foreground">
                Outstanding balance
              </p>
              <p className="mt-3 font-serif text-[28px] leading-none text-foreground">
                ${totalOutstanding.toFixed(2)}
              </p>
            </div>
            <div className="w-9 h-9 rounded-[12px] bg-destructive/10 grid place-items-center">
              <AlertCircle size={18} className="text-destructive" />
            </div>
          </div>
        </div>

        <div className="rounded-[17px] border border-card-border bg-card p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[9px] font-mono uppercase tracking-[0.1em] text-muted-foreground">
                Total invoices
              </p>
              <p className="mt-3 font-serif text-[28px] leading-none text-foreground">
                {invoices.length}
              </p>
            </div>
            <div className="w-9 h-9 rounded-[12px] bg-primary/10 grid place-items-center">
              <FileText size={18} className="text-primary" />
            </div>
          </div>
        </div>

        <div className="rounded-[17px] border border-card-border bg-card p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[9px] font-mono uppercase tracking-[0.1em] text-muted-foreground">
                Payment methods
              </p>
              <p className="mt-3 font-serif text-[28px] leading-none text-foreground">
                {paymentMethods.length}
              </p>
            </div>
            <div className="w-9 h-9 rounded-[12px] bg-accent/10 grid place-items-center">
              <CreditCard size={18} className="text-accent" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Invoices */}
        <section>
          <div className="section-heading">
            <h2>Recent invoices</h2>
            <button className="text-link">
              View all
              <ArrowRight size={14} />
            </button>
          </div>

          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-[60px] w-full" />
              ))}
            </div>
          ) : invoices.length === 0 ? (
            <EmptyState
              icon={FileText}
              title="No invoices yet"
              text="Your invoices will appear here after your first visit."
            />
          ) : (
            <div className="space-y-2">
              {invoices.map((invoice) => (
                <div
                  key={invoice.id}
                  className="flex items-center gap-4 p-4 rounded-[14px] border border-card-border bg-card hover:bg-muted/50 transition-colors"
                >
                  <div className="w-9 h-9 rounded-[10px] bg-primary/10 grid place-items-center">
                    <FileText size={16} className="text-primary" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-foreground">
                        {invoice.invoiceNumber}
                      </span>
                      <Badge
                        variant={
                          invoice.status === 'paid' ? 'success' :
                          invoice.status === 'pending' ? 'warning' : 'danger'
                        }
                      >
                        {invoice.status}
                      </Badge>
                    </div>
                    <p className="text-[11px] text-muted-foreground mt-0.5">
                      {invoice.description} · {formatDate(invoice.date)}
                    </p>
                  </div>
                  <span className="text-sm font-bold text-foreground">
                    ${invoice.amount.toFixed(2)}
                  </span>
                  <button className="icon-button subtle" aria-label="Download invoice">
                    <Download size={15} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Payment Methods */}
        <section>
          <div className="section-heading">
            <h2>Payment methods</h2>
            <button className="button button-secondary text-[10px] px-3 py-1.5 min-h-0">
              <CreditCard size={13} />
              Add method
            </button>
          </div>

          {paymentMethods.length === 0 ? (
            <EmptyState
              icon={CreditCard}
              title="No payment methods"
              text="Add a payment method for faster checkout."
            />
          ) : (
            <div className="space-y-2">
              {paymentMethods.map((method) => (
                <div
                  key={method.id}
                  className="flex items-center gap-4 p-4 rounded-[14px] border border-card-border bg-card"
                >
                  <div className="w-9 h-9 rounded-[10px] bg-accent/10 grid place-items-center">
                    <CreditCard size={16} className="text-accent" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-foreground">
                        {method.type === 'card' ? 'Card' : 'Bank account'}
                      </span>
                      <span className="text-[10px] text-muted-foreground">
                        •••• {method.last4}
                      </span>
                      {method.isDefault && (
                        <Badge variant="primary">Default</Badge>
                      )}
                    </div>
                    {method.expiry && (
                      <p className="text-[10px] text-muted-foreground mt-0.5">
                        Expires {method.expiry}
                      </p>
                    )}
                  </div>
                  {method.isDefault ? (
                    <CheckCircle2 size={16} className="text-primary" />
                  ) : (
                    <Clock3 size={16} className="text-muted-foreground" />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Insurance note */}
          <div className="mt-4 p-4 rounded-[14px] bg-secondary border border-card-border">
            <div className="flex items-start gap-3">
              <ShieldCheck size={18} className="text-primary mt-0.5" />
              <div>
                <strong className="text-xs text-foreground">Insurance information</strong>
                <p className="text-[11px] text-muted-foreground mt-1 leading-relaxed">
                  Your insurance details are managed by our billing department.
                  Contact us for updates or verification.
                </p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}