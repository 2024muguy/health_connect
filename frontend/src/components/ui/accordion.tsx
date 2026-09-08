'use client';

import { useState, type ReactNode } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AccordionItem {
  id: string;
  title: string;
  content: ReactNode;
  defaultOpen?: boolean;
}

interface AccordionProps {
  items: AccordionItem[];
  className?: string;
}

export function Accordion({ items, className }: AccordionProps) {
  const [openItems, setOpenItems] = useState<Set<string>>(
    new Set(items.filter((i) => i.defaultOpen).map((i) => i.id)),
  );

  const toggleItem = (id: string) => {
    setOpenItems((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  return (
    <div className={cn('divide-y divide-border', className)}>
      {items.map((item) => {
        const isOpen = openItems.has(item.id);
        return (
          <div key={item.id}>
            <button
              onClick={() => toggleItem(item.id)}
              className="w-full flex items-center justify-between py-4 text-left"
              aria-expanded={isOpen}
            >
              <span className="text-xs font-semibold text-foreground">{item.title}</span>
              <ChevronDown
                size={15}
                className={cn('text-muted-foreground transition-transform', isOpen && 'rotate-180')}
              />
            </button>
            {isOpen && (
              <div className="pb-4 text-xs text-muted-foreground leading-relaxed animate-rise">
                {item.content}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}