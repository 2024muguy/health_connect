/**
 * HealthConnect AI - Admin Users Page
 */

'use client';

import { useState } from 'react';
import {
  Users,
  Search,
  MoreVertical,
  ShieldCheck,
  UserRound,
  Ban,
} from 'lucide-react';
import { Avatar } from '@/components/ui/avatar';
import { SearchField } from '@/components/ui/input';
import { EmptyState } from '@/components/shared/EmptyState';
import { getInitials } from '@/lib/utils';

interface AdminUser {
  id: string;
  user_id: string;
  firstName: string;
  lastName: string;
  email: string;
  role: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export default function AdminUsersPage() {
  const [search, setSearch] = useState('');
  const [users] = useState<AdminUser[]>([]); // Would be loaded from API

  const filteredUsers = users.filter((user) => {
    const searchable = `${user.firstName || ''} ${user.lastName || ''} ${user.email}`.toLowerCase();
    return searchable.includes(search.toLowerCase());
  });

  return (
    <>
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
        <div>
          <p className="eyebrow">Administration</p>
          <h1 className="page-title">Users</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Manage patient accounts and permissions.
          </p>
        </div>
      </div>

      <div className="filter-bar">
        <SearchField value={search} onChange={setSearch} placeholder="Search users…" />
        <span className="filter-count">{filteredUsers.length} users</span>
      </div>

      {filteredUsers.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No users found"
          text={search ? 'Try a different search term.' : 'Users will appear here once registered.'}
        />
      ) : (
        <div className="rounded-[17px] border border-card-border bg-card overflow-hidden">
          <div className="divide-y divide-border">
            {filteredUsers.map((user) => (
              <div key={user.user_id} className="flex items-center gap-4 p-4 hover:bg-muted/50 transition-colors">
                <Avatar initials={getInitials(user.firstName || '', user.lastName || '')} small />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-foreground">
                      {user.firstName || ''} {user.lastName || ''}
                    </span>
                    {user.role === 'admin' && (
                      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-primary/10 text-primary text-[8px] font-mono uppercase">
                        <ShieldCheck size={10} />
                        Admin
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-muted-foreground mt-0.5">{user.email}</p>
                </div>
                <span className={`status-pill status-${user.status === 'active' ? 'confirmed' : 'cancelled'}`}>
                  <span className="status-dot" />
                  {user.status}
                </span>
                <button className="icon-button subtle" aria-label="User options">
                  <MoreVertical size={15} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}