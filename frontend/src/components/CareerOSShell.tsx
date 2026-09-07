'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import type { ReactNode, ButtonHTMLAttributes } from 'react';
import { useEffect, useMemo, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { useTheme, type CareerOSTheme } from '@/contexts/ThemeContext';

type NavItem = readonly [string, string, string];
type NavGroup = { id: string; title: string; items: NavItem[]; developerOnly?: boolean };

const groups: NavGroup[] = [
  { id: 'overview', title: 'Overview', items: [['Dashboard', '/', '⌂']] },
  { id: 'identity', title: 'Professional Identity', items: [['Profile', '/profile', '◎'], ['CV & Documents', '/documents', '▤'], ['Profile Setup', '/profile/setup', '◌'], ['Evidence Library', '/evidence-library', '▥'], ['Career Vault', '/career-vault', '◇'], ['Personas', '/personas', '◍']] },
  { id: 'connections', title: 'Connections', items: [['Organizations', '/connections/organizations', '▦'], ['Recruiters', '/connections/recruiters', '◎'], ['People', '/connections/people', '◌']] },
  { id: 'opportunity', title: 'Opportunity', items: [['Jobs', '/jobs', '▣'], ['Applications', '/applications', '☷'], ['Application Studio', '/application-studio', '✦'], ['Resume Studio', '/resume-studio', '▤'], ['Company Intelligence', '/company-intelligence', '⌁']] },
  { id: 'interview', title: 'Interview & Insight', items: [['Interview Preparation', '/interviews', '◉'], ['Live Interview', '/live-interview', '◍'], ['Interview Intelligence', '/analytics', '⌁'], ['Insights', '/insights', '◇']] },
  { id: 'global', title: 'Global', items: [['Global Intelligence', '/global-mobility', '◎']] },
  { id: 'control', title: 'Project Control', developerOnly: true, items: [['Project Control', '/project-control', '⚙']] }
];

const themes: Array<{ key: CareerOSTheme; label: string }> = [{ key: 'light', label: 'Light' }, { key: 'dark', label: 'Dark' }, { key: 'techno', label: 'Command' }];
const developerPaths = ['/project-control', '/project-tracker', '/bug-tracker', '/roadmap', '/settings/developer'];
const searchItems = groups.flatMap(group => group.items.map(([label, href]) => ({ label, href, group: group.title, developerOnly: !!group.developerOnly })));

function activeGroup(pathname: string, visibleGroups: NavGroup[]) { return visibleGroups.find(group => group.items.some(([, href]) => href === '/' ? pathname === '/' : pathname === href || pathname.startsWith(`${href}/`)))?.id || 'overview'; }
function isDeveloperPath(pathname: string) { return developerPaths.some(path => pathname === path || pathname.startsWith(`${path}/`)); }

export function CareerOSShell({ children }: { children: ReactNode }) {
  const pathname = usePathname(); const router = useRouter();
  const [user, setUser] = useState<any>(null); const [loading, setLoading] = useState(true); const [menuOpen, setMenuOpen] = useState(false); const [mobileOpen, setMobileOpen] = useState(false); const [developer, setDeveloper] = useState(false); const [search, setSearch] = useState('');
  const { theme, setTheme } = useTheme();

  useEffect(() => {
    let live = true;
    (async () => {
      if (pathname === '/login' || pathname === '/register') { setLoading(false); return; }
      if (!apiClient.hasToken()) { router.replace('/login'); return; }
      try {
        const me = await apiClient.me(); if (live) setUser(me);
        try { await apiClient.get('/api/v1/developer/status'); if (live) setDeveloper(true); }
        catch { if (live) setDeveloper(false); }
      } catch { apiClient.clearToken(); router.replace('/login'); }
      finally { if (live) setLoading(false); }
    })();
    return () => { live = false; };
  }, [pathname, router]);

  useEffect(() => { if (!loading && isDeveloperPath(pathname) && !developer) router.replace('/'); }, [loading, developer, pathname, router]);

  const visibleGroups = useMemo(() => groups.filter(group => !group.developerOnly || developer), [developer]);
  const groupId = useMemo(() => activeGroup(pathname, visibleGroups), [pathname, visibleGroups]);
  const group = visibleGroups.find(x => x.id === groupId) || visibleGroups[0];
  const searchResults = useMemo(() => { const q = search.trim().toLowerCase(); if (!q) return []; return searchItems.filter(item => (!item.developerOnly || developer) && (item.label.toLowerCase().includes(q) || item.group.toLowerCase().includes(q))).slice(0, 8); }, [search, developer]);

  if (pathname !== '/login' && pathname !== '/register' && loading) return <div className="min-h-screen grid place-items-center bg-background"><div className="techno-surface rounded-2xl border bg-card px-6 py-5 shadow-sm">Loading CareerOS…</div></div>;
  if (pathname !== '/login' && pathname !== '/register' && isDeveloperPath(pathname) && !developer) return <div className="min-h-screen grid place-items-center bg-background"><div className="rounded-2xl border bg-card px-6 py-5 text-sm text-muted-foreground">Checking developer access…</div></div>;

  const logout = () => { apiClient.clearToken(); router.replace('/login'); };
  const isActive = (href: string) => href === '/' ? pathname === '/' : pathname === href || pathname.startsWith(`${href}/`);
  const selectGroup = (next: NavGroup) => { setMobileOpen(false); router.push(next.items[0][1]); };

  return <div className="min-h-screen bg-background text-foreground">
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-[236px] border-r bg-sidebar md:flex md:flex-col">
      <div className="border-b px-4 py-4"><Link href="/" className="flex items-center gap-3"><span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary text-lg text-primary-foreground shadow-[0_0_22px_hsl(var(--primary)/.22)]">◇</span><span className="min-w-0"><strong className="block text-sm tracking-wide">CareerOS</strong><span className="block text-[11px] text-muted-foreground">Career Intelligence System</span></span></Link></div>
      <nav className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden p-3" aria-label="CareerOS domains">{visibleGroups.map(g => <button key={g.id} type="button" onClick={() => selectGroup(g)} className={`mb-2 flex w-full items-center justify-between rounded-xl px-3 py-3 text-left transition ${g.id === groupId ? 'bg-primary/10 text-primary ring-1 ring-primary/20' : 'text-muted-foreground hover:bg-muted/70 hover:text-foreground'}`}><span><span className="block text-[10px] font-bold uppercase tracking-[.17em]">{g.title}</span><span className="mt-1 block text-[11px] opacity-70">{g.items.length} workspace {g.items.length === 1 ? 'area' : 'areas'}</span></span><span className="text-xs">{g.id === groupId ? '●' : '○'}</span></button>)}</nav>
      <div className="border-t p-3"><div className="rounded-xl border bg-card/70 p-2.5"><div className="flex items-center gap-3"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-primary/10 text-xs font-bold text-primary ring-1 ring-primary/15">{(user?.name || user?.email || 'A').slice(0, 1).toUpperCase()}</span><span className="min-w-0"><span className="block truncate text-xs font-semibold">{user?.name || 'Personal Workspace'}</span><span className="block truncate text-[11px] text-muted-foreground">{user?.email || 'CareerOS'}</span></span></div><button onClick={logout} className="mt-2 w-full rounded-lg border bg-background px-2 py-2 text-xs font-semibold transition hover:bg-muted">Sign out</button></div></div>
    </aside>

    <div className="md:pl-[236px]">
      <header className="sticky top-0 z-30 border-b bg-background/90 backdrop-blur-xl">
        <div className="flex min-h-[68px] items-center gap-3 px-4 py-2 sm:px-6">
          <button className="grid h-9 w-9 place-items-center rounded-lg border bg-card/60 md:hidden" onClick={() => setMobileOpen(v => !v)} aria-label="Open application navigation">☰</button>
          <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-primary/10 text-xs font-bold text-primary ring-1 ring-primary/20">{(user?.name || user?.email || 'A').slice(0, 1).toUpperCase()}</div>
          <div className="min-w-0 flex-1"><p className="truncate text-sm font-bold">{user?.name || 'CareerOS'}</p><p className="hidden truncate text-[11px] text-muted-foreground sm:block">Professional identity · evidence-first career operating system</p></div>
          <div className="relative hidden w-full max-w-[360px] sm:block"><div className="flex items-center rounded-xl border bg-card/70 px-3 py-2 shadow-sm"><span className="mr-2 text-sm text-muted-foreground">⌕</span><input value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => { if (e.key === 'Escape') setSearch(''); if (e.key === 'Enter' && searchResults[0]) { setSearch(''); router.push(searchResults[0].href); } }} placeholder="Search CareerOS" aria-label="Search CareerOS" className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"/><kbd className="hidden rounded-md border px-1.5 py-0.5 text-[10px] text-muted-foreground lg:block">/</kbd></div>{searchResults.length > 0 && <div className="absolute right-0 top-12 z-50 w-full overflow-hidden rounded-xl border bg-card shadow-2xl">{searchResults.map(item => <button key={`${item.group}-${item.href}`} type="button" onClick={() => { setSearch(''); router.push(item.href); }} className="flex w-full items-center justify-between px-3 py-2.5 text-left text-sm hover:bg-muted"><span>{item.label}</span><span className="text-[10px] text-muted-foreground">{item.group}</span></button>)}</div>}</div>
          <div className="relative shrink-0"><button type="button" aria-label="User account menu" onClick={() => setMenuOpen(v => !v)} className="grid h-10 w-10 place-items-center rounded-xl border bg-card/60 text-lg font-semibold transition hover:border-primary/40 hover:bg-muted">⋮</button>{menuOpen && <div className="absolute right-0 top-12 z-50 w-72 rounded-2xl border bg-card p-2 shadow-2xl"><div className="border-b px-3 py-2"><p className="text-xs font-semibold">{user?.name || 'CareerOS account'}</p><p className="mt-0.5 truncate text-[11px] text-muted-foreground">{user?.email || ''}</p></div><Link onClick={() => setMenuOpen(false)} href="/profile" className="mt-1 block rounded-lg px-3 py-2 text-sm hover:bg-muted">My Profile</Link><Link onClick={() => setMenuOpen(false)} href="/settings?section=account" className="block rounded-lg px-3 py-2 text-sm hover:bg-muted">Account & Security</Link><div className="mt-1 rounded-lg border bg-background/40 p-2"><p className="px-2 py-1 text-[10px] font-bold uppercase tracking-[.16em] text-muted-foreground">Appearance</p><div className="mt-1 grid grid-cols-3 gap-1">{themes.map(t => <button key={t.key} type="button" onClick={() => setTheme(t.key)} className={`rounded-lg px-2 py-2 text-[11px] font-semibold transition ${theme === t.key ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}>{t.label}</button>)}</div></div><Link onClick={() => setMenuOpen(false)} href="/settings" className="mt-1 block rounded-lg px-3 py-2 text-sm hover:bg-muted">Application Settings</Link><button onClick={logout} className="mt-1 w-full rounded-lg px-3 py-2 text-left text-sm text-red-500 hover:bg-muted">Sign out</button></div>}</div>
        </div>
        <div className="border-t bg-card/25 px-3 py-2 sm:px-4"><div className="flex items-center gap-2"><div className="hidden shrink-0 px-2 text-[10px] font-bold uppercase tracking-[.18em] text-muted-foreground lg:block">{group?.title}</div><nav className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto pb-0.5" aria-label={`${group?.title || 'CareerOS'} workspace`}>{group?.items.map(([label, href, icon]) => <Link key={href} href={href} title={label} className={`flex min-w-max items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold transition ${isActive(href) ? 'bg-primary/10 text-primary shadow-[inset_0_-2px_0_hsl(var(--primary))]' : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'}`}><span className="text-[11px] opacity-90" aria-hidden="true">{icon}</span><span>{label}</span></Link>)}</nav></div></div>
      </header>
      {mobileOpen && <div className="fixed inset-0 z-50 bg-background/95 p-4 backdrop-blur-xl md:hidden"><div className="mb-4 flex items-center justify-between"><p className="font-semibold">CareerOS navigation</p><button onClick={() => setMobileOpen(false)} className="grid h-9 w-9 place-items-center rounded-lg border" aria-label="Close navigation">×</button></div><div className="mb-4 grid gap-2 sm:grid-cols-2">{visibleGroups.map(g => <button key={g.id} onClick={() => selectGroup(g)} className={`rounded-xl border px-3 py-3 text-left ${g.id === groupId ? 'border-primary bg-primary/10 text-primary' : 'bg-card text-muted-foreground'}`}><span className="block text-[10px] font-bold uppercase tracking-[.17em]">{g.title}</span></button>)}</div><div className="max-h-[calc(100vh-13rem)] overflow-auto rounded-xl border bg-card p-2">{group?.items.map(([label, href, icon]) => <Link key={href} href={href} onClick={() => setMobileOpen(false)} className={`flex items-center gap-3 rounded-lg px-3 py-3 text-sm ${isActive(href) ? 'bg-primary/10 font-semibold text-primary' : 'text-muted-foreground hover:bg-muted'}`}><span aria-hidden="true">{icon}</span>{label}</Link>)}</div></div>}
      <main className="min-h-[calc(100vh-7rem)] px-4 py-6 sm:px-6 lg:px-8"><div className="mx-auto w-full max-w-[1440px]">{children}</div></main>
    </div>
  </div>;
}

export function PageHeader({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: ReactNode }) { return <header className="mb-6 flex flex-col gap-4 border-b pb-6 sm:flex-row sm:items-end sm:justify-between"><div><p className="text-xs font-semibold uppercase tracking-[.16em] text-primary">{eyebrow}</p><h1 className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">{title}</h1><p className="mt-2 max-w-3xl text-sm text-muted-foreground">{description}</p></div>{action}</header>; }
export function Card({ title, children, className = '' }: { title?: string; children: ReactNode; className?: string }) { return <section className={`techno-surface rounded-2xl border bg-card shadow-sm ${className}`}>{title && <div className="border-b px-5 py-4"><h2 className="text-sm font-semibold">{title}</h2></div>}<div className="p-5">{children}</div></section>; }
export function Badge({ children, tone = 'muted' }: { children: ReactNode; tone?: 'muted' | 'good' | 'warn' | 'blue' }) { const c = { muted: 'bg-muted text-muted-foreground', good: 'bg-emerald-500/10 text-emerald-500', warn: 'bg-amber-500/10 text-amber-500', blue: 'bg-primary/10 text-primary' }[tone]; return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${c}`}>{children}</span>; }
export function Button({ children, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) { return <button {...props} className={`rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50 ${props.className || ''}`}>{children}</button>; }
