'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Search, X, Calendar, MessageCircle, Stethoscope, Info } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { cn } from '@/lib/utils';

interface SearchResult {
  id: string;
  type: 'service' | 'appointment' | 'conversation' | 'clinic';
  title: string;
  subtitle?: string;
  href: string;
}

export function SearchBar({ className }: { className?: string }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [allData, setAllData] = useState<SearchResult[]>([]);
  const [highlighted, setHighlighted] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load searchable data once
  useEffect(() => {
    const load = async () => {
      const items: SearchResult[] = [];
      try {
        const [services, appts, convs] = await Promise.all([
          apiClient.get<any>('/clinic/services').catch(() => null),
          apiClient.get<any>('/appointments').catch(() => null),
          apiClient.get<any>('/chat/conversations').catch(() => null),
        ]);

        // Services
        const svcList = Array.isArray(services) ? services : services?.services ?? [];
        for (const s of svcList) {
          const name = typeof s === 'string' ? s : s?.name;
          if (!name) continue;
          items.push({
            id: `svc-${name}`,
            type: 'service',
            title: name,
            subtitle: 'Clinic service',
            href: '/appointments/new',
          });
        }

        // Appointments
        const apptList = Array.isArray(appts) ? appts : appts?.appointments ?? [];
        for (const a of apptList.slice(0, 10)) {
          items.push({
            id: `appt-${a.id || a.appointment_id}`,
            type: 'appointment',
            title: a.appointment_type || 'Appointment',
            subtitle: a.appointment_date || a.scheduled_datetime || '',
            href: '/appointments',
          });
        }

        // Conversations
        const convList = Array.isArray(convs) ? convs : convs?.conversations ?? [];
        for (const c of convList.slice(0, 10)) {
          items.push({
            id: `conv-${c.id || c.conversation_id}`,
            type: 'conversation',
            title: c.title || `Conversation ${c.conversation_code || c.id}`,
            subtitle: c.preview || 'Chat',
            href: `/chat/${c.id || c.conversation_id}`,
          });
        }

        // Static links
        items.push(
          { id: 'nav-clinic', type: 'clinic', title: 'Clinic Information', subtitle: 'Hours, location, contacts', href: '/clinic' },
          { id: 'nav-appts', type: 'clinic', title: 'My Appointments', subtitle: 'Upcoming and past visits', href: '/appointments' },
          { id: 'nav-chat', type: 'clinic', title: 'Care Assistant', subtitle: 'Ask about your care', href: '/chat' },
          { id: 'nav-profile', type: 'clinic', title: 'My Profile', subtitle: 'Account settings', href: '/profile' },
        );

        setAllData(items);
      } catch (err) {
        console.error('[SearchBar] load failed', err);
      }
    };
    load();
  }, []);

  // Filter results
  useEffect(() => {
    if (!query.trim()) {
      setResults(allData.slice(0, 8));
      setHighlighted(0);
      return;
    }
    const q = query.toLowerCase();
    const filtered = allData
      .filter(
        (r) =>
          r.title.toLowerCase().includes(q) ||
          (r.subtitle || '').toLowerCase().includes(q)
      )
      .slice(0, 10);
    setResults(filtered);
    setHighlighted(0);
  }, [query, allData]);

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // ⌘K or Ctrl+K to open
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(true);
        setTimeout(() => inputRef.current?.focus(), 50);
      }
      if (e.key === 'Escape') {
        setOpen(false);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  const go = (result: SearchResult) => {
    router.push(result.href);
    setOpen(false);
    setQuery('');
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlighted((h) => Math.min(h + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlighted((h) => Math.max(h - 1, 0));
    } else if (e.key === 'Enter' && results[highlighted]) {
      e.preventDefault();
      go(results[highlighted]);
    }
  };

  const iconFor = (type: string) => {
    switch (type) {
      case 'service': return <Stethoscope size={14} />;
      case 'appointment': return <Calendar size={14} />;
      case 'conversation': return <MessageCircle size={14} />;
      default: return <Info size={14} />;
    }
  };

  return (
    <div ref={ref} className={cn('relative hidden md:block', className)}>
      {/* Trigger */}
      <button
        type="button"
        onClick={() => {
          setOpen(true);
          setTimeout(() => inputRef.current?.focus(), 50);
        }}
        className="flex items-center gap-2 px-3 h-9 rounded-lg bg-muted/50 hover:bg-muted border border-border/50 text-xs text-muted-foreground transition-colors"
        aria-label="Search"
        data-testid="button-search"
      >
        <Search size={14} />
        <span className="min-w-[120px] text-left">Search…</span>
        <kbd className="ml-2 px-1.5 py-0.5 rounded bg-background border border-border text-[9px] font-mono">
          ⌘K
        </kbd>
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute right-0 mt-2 w-96 bg-card border border-border rounded-xl shadow-lg z-50 overflow-hidden">
          {/* Input */}
          <div className="flex items-center gap-2 px-3 py-2 border-b border-border">
            <Search size={14} className="text-muted-foreground" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder="Search services, appointments, chats…"
              className="flex-1 bg-transparent text-sm outline-none"
              autoFocus
            />
            {query && (
              <button onClick={() => setQuery('')} className="text-muted-foreground hover:text-foreground">
                <X size={14} />
              </button>
            )}
          </div>

          {/* Results */}
          <div className="max-h-96 overflow-y-auto py-1">
            {results.length === 0 ? (
              <div className="px-4 py-6 text-center text-xs text-muted-foreground">
                No results for "{query}"
              </div>
            ) : (
              results.map((r, i) => (
                <button
                  key={r.id}
                  onClick={() => go(r)}
                  onMouseEnter={() => setHighlighted(i)}
                  className={cn(
                    'w-full text-left px-4 py-2.5 flex items-center gap-3 transition-colors',
                    i === highlighted ? 'bg-primary/10' : 'hover:bg-muted/50'
                  )}
                >
                  <span className="w-7 h-7 rounded-md bg-muted flex items-center justify-center text-muted-foreground">
                    {iconFor(r.type)}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-foreground truncate">{r.title}</div>
                    {r.subtitle && (
                      <div className="text-[11px] text-muted-foreground truncate">{r.subtitle}</div>
                    )}
                  </div>
                </button>
              ))
            )}
          </div>

          {/* Footer hint */}
          <div className="border-t border-border px-3 py-2 text-[10px] text-muted-foreground flex items-center gap-3">
            <span>↑↓ navigate</span>
            <span>↵ select</span>
            <span>esc close</span>
          </div>
        </div>
      )}
    </div>
  );
}
