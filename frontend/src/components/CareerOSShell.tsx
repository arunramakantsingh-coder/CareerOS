'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import type { ReactNode, ButtonHTMLAttributes } from 'react';
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { useTheme } from '@/contexts/ThemeContext';

type NavItem = readonly [string, string, string];
type NavGroup = { title: string; items: NavItem[] };

const groups: NavGroup[] = [
  { title: 'Overview', items: [['Home', '/', '⌂']] },
  { title: 'My Career', items: [['Profile', '/profile', '◎'], ['Career Vault', '/career-vault', '◇'], ['Documents', '/documents', '▤'], ['Personas', '/personas', '◌']] },
  { title: 'Opportunity', items: [['Jobs', '/jobs', '▣'], ['Applications', '/applications', '☷'], ['Application Studio', '/application-studio', '✦'], ['Resume Studio', '/resume-studio', '▤'], ['Company Intelligence', '/company-intelligence', '⌁'], ['Interviews', '/interviews', '◉'], ['Live Interview', '/live-interview', '◍'], ['Global Mobility', '/global-mobility', '◎']] },
  { title: 'Intelligence', items: [['Analytics', '/analytics', '▥'], ['Settings', '/settings', '⚙']] },
];

function initials(value: string) {
  return value.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase() || 'A';
}

export function CareerOSShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let live = true;
    (async () => {
      if (pathname === '/login' || pathname === '/register') { setLoading(false); return; }
      if (!apiClient.hasToken()) { router.replace('/login'); return; }
      try { const me = await apiClient.me(); if (live) setUser(me); }
      catch { apiClient.clearToken(); router.replace('/login'); }
      finally { if (live) setLoading(false); }
    })();
    return () => { live = false; };
  }, [pathname, router]);

  if ((pathname !== '/login' && pathname !== '/register') && loading) {
    return <div className="min-h-screen grid place-items-center bg-background"><div className="rounded-2xl border bg-card px-6 py-5 shadow-sm">Loading CareerOS…</div></div>;
  }

  if (pathname === '/login' || pathname === '/register') return <>{children}</>;

  const displayName = user?.name || user?.email || 'Career Professional';
  const logout = () => { apiClient.clearToken(); router.replace('/login'); };

  return <div className="min-h-screen bg-background text-foreground">
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 border-r bg-sidebar md:flex md:flex-col">
      <div className="border-b px-4 py-4">
        <Link href="/" className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-primary text-primary-foreground text-lg shadow-sm">◈</span>
          <span><strong className="block text-sm tracking-wide">CareerOS</strong><span className="text-[11px] text-muted-foreground">Career Intelligence System</span></span>
        </Link>
      </div>
      <nav className="flex-1 overflow-y-auto p-3">
        {groups.map((group) => <div key={group.title} className="mb-5">
          <p className="px-2 pb-2 text-[10px] font-semibold uppercase tracking-[.18em] text-muted-foreground">{group.title}</p>
          <div className="space-y-1">
            {group.items.map(([label, href, icon]) => {
              const active = pathname === href || (href !== '/' && pathname.startsWith(href + '/'));
              return <Link key={href} href={href} className={`flex h-10 items-center gap-3 rounded-xl px-3 text-sm transition ${active ? 'bg-primary/10 font-semibold text-primary shadow-sm' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}>
                <span className="w-5 text-center text-base">{icon}</span>{label}
              </Link>;
            })}
          </div>
        </div>)}
      </nav>
      <div className="border-t p-3">
        <div className="rounded-2xl bg-muted/60 p-3">
          <div className="flex items-center gap-3"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-primary/10 text-xs font-bold text-primary">{initials(displayName)}</span><span className="min-w-0"><span className="block truncate text-xs font-semibold">{displayName}</span><span className="block truncate text-[11px] text-muted-foreground">{user?.email || 'Professional workspace'}</span></span></div>
          <button onClick={logout} className="mt-3 w-full rounded-lg border bg-background px-2 py-2 text-xs font-semibold hover:bg-muted">Sign out</button>
        </div>
      </div>
    </aside>

    <div className="md:pl-64">
      <header className="sticky top-0 z-30 border-b bg-background/90 px-4 py-2.5 backdrop-blur sm:px-6">
        <div className="flex items-center gap-3">
          <Link href="/profile" className="flex min-w-0 flex-1 items-center gap-3 rounded-xl px-1 py-1">
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-primary/10 text-xs font-bold text-primary ring-1 ring-primary/15">{initials(displayName)}</span>
            <span className="min-w-0"><span className="block truncate text-sm font-semibold">{displayName}</span><span className="hidden truncate text-xs text-muted-foreground sm:block">Your professional identity · evidence-first career workspace</span></span>
          </Link>
          <div className="hidden items-center gap-1 rounded-xl border bg-muted/40 p-1 sm:flex">
            {(['light', 'dark', 'techno'] as const).map((item) => <button key={item} onClick={() => setTheme(item)} className={`rounded-lg px-2.5 py-1.5 text-[11px] font-semibold capitalize ${theme === item ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}>{item}</button>)}
          </div>
          <Link href="/settings" className="rounded-xl border px-3 py-2 text-xs font-semibold hover:bg-muted">Settings</Link>
        </div>
        <nav className="career-top-nav mt-2 hidden gap-1 overflow-x-auto pb-0.5 lg:flex">
          {groups.flatMap((group) => group.items.slice(0, group.title === 'Opportunity' ? 6 : group.items.length)).map(([label, href]) => {
            const active = pathname === href || (href !== '/' && pathname.startsWith(href + '/'));
            return <Link key={href} href={href} className={`whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-medium ${active ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}>{label}</Link>;
          })}
        </nav>
      </header>

      <div className="border-b bg-background px-3 py-2 md:hidden"><select value={pathname} onChange={(e) => router.push(e.target.value)} className="w-full rounded-xl border bg-background px-3 py-2.5 text-sm font-medium">{groups.flatMap((g) => g.items).map(([label, href]) => <option key={href} value={href}>{label}</option>)}</select></div>
      <main className="min-h-[calc(100vh-6rem)] px-4 py-6 pb-24 sm:px-6 lg:px-8"><div className="mx-auto w-full max-w-7xl">{children}</div></main>

      <nav className="fixed inset-x-0 bottom-0 z-40 border-t bg-background/95 p-2 backdrop-blur md:hidden"><div className="grid grid-cols-4 gap-1">
        {[['Home', '/'], ['Profile', '/profile'], ['Vault', '/career-vault'], ['Jobs', '/jobs']].map(([label, href]) => <Link key={href} href={href} className={`rounded-xl py-2 text-center text-[11px] font-semibold ${pathname === href ? 'bg-primary/10 text-primary' : 'text-muted-foreground'}`}>{label}</Link>)}
      </div></nav>
    </div>
  </div>;
}

export function PageHeader({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: ReactNode }) {
  return <header className="mb-6 flex flex-col gap-4 border-b pb-6 sm:flex-row sm:items-end sm:justify-between"><div><p className="text-xs font-semibold uppercase tracking-[.16em] text-primary">{eyebrow}</p><h1 className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">{title}</h1><p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">{description}</p></div>{action}</header>;
}

export function Card({ title, children, className = '' }: { title?: string; children: ReactNode; className?: string }) {
  return <section className={`rounded-2xl border bg-card shadow-sm ${className}`}>{title && <div className="border-b px-5 py-4"><h2 className="text-sm font-semibold">{title}</h2></div>}<div className="p-5">{children}</div></section>;
}

export function Badge({ children, tone = 'muted' }: { children: ReactNode; tone?: 'muted' | 'good' | 'warn' | 'blue' }) {
  const classes = { muted: 'bg-muted text-muted-foreground', good: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300', warn: 'bg-amber-500/10 text-amber-700 dark:text-amber-300', blue: 'bg-primary/10 text-primary' }[tone];
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${classes}`}>{children}</span>;
}

export function Button({ children, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button {...props} className={`rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50 ${props.className || ''}`}>{children}</button>;
}
