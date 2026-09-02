'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import type { ReactNode, ButtonHTMLAttributes } from 'react';
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { useTheme, type CareerOSTheme } from '@/contexts/ThemeContext';

type NavItem = readonly [string,string,string];
type NavGroup = { title: string; items: NavItem[] };

const groups: NavGroup[] = [
  { title:'Overview', items:[['Dashboard','/','⌂']] },
  { title:'Professional Identity', items:[['Profile','/profile','◎'],['Profile Setup','/onboarding','◌'],['Profile Intelligence','/profile/intelligence','✦'],['CV & Documents','/documents','▤'],['Career Vault','/career-vault','◇'],['Personas','/personas','◍']] },
  { title:'Opportunity', items:[['Jobs','/jobs','▣'],['Applications','/applications','☷'],['Application Studio','/application-studio','✦'],['Resume Studio','/resume-studio','▤'],['Company Intelligence','/company-intelligence','⌁']] },
  { title:'Interview & Insight', items:[['Interviews','/interviews','◉'],['Live Interview','/live-interview','◍'],['Analytics','/analytics','⌁']] },
  { title:'Global', items:[['Global Mobility','/global-mobility','◎']] },
];

// The horizontal strip is intentionally NOT a second copy of the sidebar.
// It represents the user's career journey at a glance; the sidebar remains the
// detailed application/module navigator.
const journeyNav: NavItem[] = [
  ['Home','/','⌂'],
  ['Build','/profile','◎'],
  ['Discover','/jobs','⌕'],
  ['Apply','/applications','↗'],
  ['Interview','/live-interview','◉'],
  ['Insights','/analytics','✦'],
];

const themes: Array<{key: CareerOSTheme; label: string}> = [
  { key:'light', label:'Light' }, { key:'dark', label:'Dark' }, { key:'techno', label:'Command' },
];

export function CareerOSShell({children}:{children:ReactNode}){
  const pathname=usePathname(); const router=useRouter();
  const [user,setUser]=useState<any>(null); const [loading,setLoading]=useState(true); const [menuOpen,setMenuOpen]=useState(false);
  const { theme, setTheme } = useTheme();

  useEffect(()=>{ let live=true; (async()=>{
    if(pathname==='/login' || pathname==='/register'){setLoading(false);return;}
    if(!apiClient.hasToken()){router.replace('/login');return;}
    try{const me=await apiClient.me(); if(live)setUser(me);}
    catch{apiClient.clearToken(); router.replace('/login');}
    finally{if(live)setLoading(false);}
  })(); return()=>{live=false}; },[pathname,router]);

  if((pathname!=='/login' && pathname!=='/register') && loading) return <div className="min-h-screen grid place-items-center bg-background"><div className="techno-surface rounded-2xl border bg-card px-6 py-5 shadow-sm">Loading CareerOS…</div></div>;
  const logout=()=>{apiClient.clearToken();router.replace('/login')};
  const isActive=(href:string)=>pathname===href || (href!=='/' && pathname.startsWith(href+'/'));

  return <div className="min-h-screen bg-background text-foreground">
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-[282px] border-r bg-sidebar md:flex md:flex-col">
      <div className="border-b px-4 py-4">
        <Link href="/" className="flex items-center gap-3">
          <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary text-primary-foreground text-lg shadow-[0_0_22px_hsl(var(--primary)/.22)]">◇</span>
          <span className="min-w-0"><strong className="block text-sm tracking-wide">CareerOS</strong><span className="block text-[11px] text-muted-foreground">Career Intelligence System</span></span>
        </Link>
      </div>

      <nav className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden p-3">
        {groups.map(g=><div key={g.title} className="mb-5">
          <p className="px-2 pb-2 text-[10px] font-bold uppercase tracking-[.18em] text-muted-foreground">{g.title}</p>
          <div className="space-y-1">{g.items.map(([label,href,icon])=>{const active=isActive(href);return <Link key={href} href={href} className={`group flex h-10 items-center gap-3 rounded-lg px-3 text-sm transition ${active?'bg-primary/10 font-semibold text-primary shadow-[inset_2px_0_0_hsl(var(--primary))]':'text-muted-foreground hover:bg-muted/70 hover:text-foreground'}`}><span className="w-4 text-center text-sm opacity-90">{icon}</span>{label}</Link>})}</div>
        </div>)}
      </nav>

      <div className="border-t p-3"><div className="rounded-xl border bg-card/70 p-2.5">
        <div className="flex items-center gap-3"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-primary/10 text-xs font-bold text-primary ring-1 ring-primary/15">{(user?.name||user?.email||'A').slice(0,1).toUpperCase()}</span><span className="min-w-0"><span className="block truncate text-xs font-semibold">{user?.name||'Personal Workspace'}</span><span className="block truncate text-[11px] text-muted-foreground">{user?.email||'CareerOS'}</span></span></div>
        <button onClick={logout} className="mt-2 w-full rounded-lg border bg-background px-2 py-2 text-xs font-semibold transition hover:bg-muted">Sign out</button>
      </div></div>
    </aside>

    <div className="md:pl-[282px]">
      <header className="sticky top-0 z-30 border-b bg-background/90 backdrop-blur-xl">
        <div className="flex min-h-[68px] items-center gap-3 px-4 py-2 sm:px-6">
          <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-primary/10 text-xs font-bold text-primary ring-1 ring-primary/20">{(user?.name||user?.email||'A').slice(0,1).toUpperCase()}</div>
          <div className="min-w-0 flex-1"><p className="truncate text-sm font-bold">{user?.name||'CareerOS'}</p><p className="hidden truncate text-[11px] text-muted-foreground sm:block">Professional identity · evidence-first career operating system</p></div>
          <div className="hidden items-center rounded-xl border bg-card/60 p-1 lg:flex">{themes.map(t=><button key={t.key} type="button" onClick={()=>setTheme(t.key)} className={`rounded-lg px-3 py-1.5 text-[11px] font-semibold transition ${theme===t.key?'bg-primary text-primary-foreground shadow-sm':'text-muted-foreground hover:text-foreground'}`}>{t.label}</button>)}</div>
          <Link href="/settings" className="rounded-lg border bg-card/60 px-3 py-2 text-xs font-semibold transition hover:bg-muted">Settings</Link>
          <div className="relative"><button type="button" aria-label="More application options" onClick={()=>setMenuOpen(v=>!v)} className="grid h-9 w-9 place-items-center rounded-lg border bg-card/60 text-lg hover:bg-muted">⋮</button>{menuOpen&&<div className="absolute right-0 top-11 w-56 rounded-xl border bg-card p-2 shadow-xl"><Link onClick={()=>setMenuOpen(false)} href="/profile" className="block rounded-lg px-3 py-2 text-sm hover:bg-muted">Professional identity</Link><Link onClick={()=>setMenuOpen(false)} href="/profile/intelligence" className="block rounded-lg px-3 py-2 text-sm hover:bg-muted">Profile intelligence</Link><Link onClick={()=>setMenuOpen(false)} href="/settings" className="block rounded-lg px-3 py-2 text-sm hover:bg-muted">Application settings</Link><button onClick={logout} className="mt-1 w-full rounded-lg px-3 py-2 text-left text-sm text-red-500 hover:bg-muted">Sign out</button></div>}</div>
        </div>

        <div className="border-t bg-card/20 px-3 py-2 sm:px-4">
          <nav className="flex items-center gap-1 overflow-x-auto pb-0.5" aria-label="Career journey">
            {journeyNav.map(([label,href,icon])=>{
              const active=isActive(href);
              return <Link key={href} href={href} title={label} className={`group flex min-w-max items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold transition ${active?'bg-primary/10 text-primary shadow-[inset_0_-2px_0_hsl(var(--primary))]':'text-muted-foreground hover:bg-muted/60 hover:text-foreground'}`}>
                <span className="text-[11px] opacity-90">{icon}</span><span>{label}</span>
              </Link>;
            })}
          </nav>
        </div>
      </header>

      <div className="border-b bg-background px-3 py-2 md:hidden"><select value={pathname} onChange={e=>router.push(e.target.value)} className="w-full rounded-lg border bg-card px-3 py-2.5 text-sm">{[...groups.flatMap(g=>g.items),['Settings','/settings','⚙'] as NavItem].map(([label,href])=><option key={href} value={href}>{label}</option>)}</select></div>
      <main className="min-h-[calc(100vh-7rem)] px-4 py-6 sm:px-6 lg:px-8"><div className="mx-auto w-full max-w-[1440px]">{children}</div></main>
    </div>
  </div>
}

export function PageHeader({eyebrow,title,description,action}:{eyebrow:string;title:string;description:string;action?:ReactNode}){return <header className="mb-6 flex flex-col gap-4 border-b pb-6 sm:flex-row sm:items-end sm:justify-between"><div><p className="text-xs font-semibold uppercase tracking-[.16em] text-primary">{eyebrow}</p><h1 className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">{title}</h1><p className="mt-2 max-w-3xl text-sm text-muted-foreground">{description}</p></div>{action}</header>}
export function Card({title,children,className='' }:{title?:string;children:ReactNode;className?:string}){return <section className={`techno-surface rounded-xl border bg-card shadow-sm ${className}`}>{title&&<div className="border-b px-5 py-4"><h2 className="text-sm font-semibold">{title}</h2></div>}<div className="p-5">{children}</div></section>}
export function Badge({children,tone='muted'}:{children:ReactNode;tone?:'muted'|'good'|'warn'|'blue'}){const c={muted:'bg-muted text-muted-foreground',good:'bg-emerald-500/10 text-emerald-500',warn:'bg-amber-500/10 text-amber-500',blue:'bg-primary/10 text-primary'}[tone];return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${c}`}>{children}</span>}
export function Button({children,...props}:ButtonHTMLAttributes<HTMLButtonElement>){return <button {...props} className={`rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50 ${props.className||''}`}>{children}</button>}
