 'use client';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import type { ReactNode, ButtonHTMLAttributes } from 'react';
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';

type NavItem = readonly [string,string,string];
type NavGroup = { title: string; items: NavItem[] };
const groups: NavGroup[] = [
  { title:'Overview', items:[['Dashboard','/','▦']] },
  { title:'Career', items:[['Career Vault','/career-vault','◇'],['Personas','/personas','◎']] },
  { title:'Opportunity', items:[['Jobs','/jobs','▣'],['Applications','/applications','☷'],['Application Studio','/application-studio','✦'],['Resume Studio','/resume-studio','▤'],['Company Intelligence','/company-intelligence','⌂'],['Interviews','/interviews','◌'],['Live Interview','/live-interview','◉'],['Global Mobility','/global-mobility','◎']] },
  { title:'System', items:[['Analytics','/analytics','▥'],['Settings','/settings','⚙']] },
] as const;

export function CareerOSShell({children}:{children:ReactNode}){
  const pathname=usePathname(); const router=useRouter(); const [user,setUser]=useState<any>(null); const [loading,setLoading]=useState(true);
  useEffect(()=>{ let live=true; (async()=>{ if(pathname==='/login'){setLoading(false);return;} if(!apiClient.hasToken()){router.replace('/login');return;} try{const me=await apiClient.me(); if(live)setUser(me);}catch{apiClient.clearToken(); router.replace('/login');}finally{if(live)setLoading(false);}})(); return()=>{live=false}; },[pathname,router]);
  if(pathname!=='/login' && loading) return <div className="min-h-screen grid place-items-center bg-background"><div className="rounded-xl border bg-card px-6 py-5 shadow-sm">Loading CareerOS…</div></div>;
  const logout=()=>{apiClient.clearToken();router.replace('/login')};
  return <div className="min-h-screen bg-background text-foreground">
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 border-r bg-sidebar md:flex md:flex-col">
      <div className="border-b px-4 py-4"><Link href="/" className="flex items-center gap-3"><span className="grid h-9 w-9 place-items-center rounded-lg bg-primary text-primary-foreground text-lg">◈</span><span><strong className="block text-sm">CareerOS</strong><span className="text-[11px] text-muted-foreground">Personal Job & Interview Copilot</span></span></Link></div>
      <nav className="flex-1 overflow-y-auto p-3">{groups.map(g=><div key={g.title} className="mb-5"><p className="px-2 pb-2 text-[11px] font-semibold uppercase tracking-[.14em] text-muted-foreground">{g.title}</p><div className="space-y-1">{g.items.map(([label,href,icon])=>{const active=pathname===href||((href!=='/'&&pathname.startsWith(href+'/')));return <Link key={href} href={href} className={`flex h-9 items-center gap-3 rounded-md px-3 text-sm transition ${active?'bg-primary/10 font-medium text-primary':'text-muted-foreground hover:bg-muted hover:text-foreground'}`}><span className="w-4 text-center">{icon}</span>{label}</Link>})}</div></div>)}</nav>
      <div className="border-t p-3"><div className="rounded-md bg-muted/60 p-2"><div className="flex items-center gap-3"><span className="grid h-8 w-8 place-items-center rounded-full bg-primary/10 text-xs font-semibold text-primary">{(user?.name||user?.email||'A').slice(0,1).toUpperCase()}</span><span className="min-w-0"><span className="block truncate text-xs font-medium">{user?.name||'Personal Workspace'}</span><span className="block truncate text-[11px] text-muted-foreground">{user?.email||'v0.1 Copilot'}</span></span></div><button onClick={logout} className="mt-2 w-full rounded-md border bg-background px-2 py-1.5 text-xs font-medium hover:bg-muted">Sign out</button></div></div>
    </aside>
    <div className="md:pl-64"><header className="sticky top-0 z-30 flex min-h-14 items-center gap-3 border-b bg-background/90 px-4 py-2 backdrop-blur sm:px-6"><div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">CareerOS</p><p className="hidden text-xs text-muted-foreground sm:block">Your evidence-first AI career workspace</p></div><Link href="/onboarding" className="hidden rounded-full border border-primary/20 bg-primary/5 px-2.5 py-1 text-xs font-medium text-primary sm:inline-flex">Setup</Link><Link href="/settings" className="rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-muted">Settings</Link></header>
      <div className="border-b bg-background px-3 py-2 md:hidden"><select value={pathname} onChange={e=>router.push(e.target.value)} className="w-full rounded-md border bg-background px-3 py-2 text-sm">{groups.flatMap(g=>g.items).map(([label,href])=><option key={href} value={href}>{label}</option>)}</select></div>
      <main className="min-h-[calc(100vh-3.5rem)] px-4 py-6 sm:px-6 lg:px-8"><div className="mx-auto w-full max-w-7xl">{children}</div></main></div>
  </div>
}
export function PageHeader({eyebrow,title,description,action}:{eyebrow:string;title:string;description:string;action?:ReactNode}){return <header className="mb-6 flex flex-col gap-4 border-b pb-6 sm:flex-row sm:items-end sm:justify-between"><div><p className="text-xs font-semibold uppercase tracking-[.14em] text-muted-foreground">{eyebrow}</p><h1 className="mt-1 text-3xl font-bold tracking-tight">{title}</h1><p className="mt-2 max-w-3xl text-sm text-muted-foreground">{description}</p></div>{action}</header>}
export function Card({title,children,className='' }:{title?:string;children:ReactNode;className?:string}){return <section className={`rounded-xl border bg-card shadow-sm ${className}`}>{title&&<div className="border-b px-5 py-4"><h2 className="text-sm font-semibold">{title}</h2></div>}<div className="p-5">{children}</div></section>}
export function Badge({children,tone='muted'}:{children:ReactNode;tone?:'muted'|'good'|'warn'|'blue'}){const c={muted:'bg-muted text-muted-foreground',good:'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300',warn:'bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300',blue:'bg-primary/10 text-primary'}[tone];return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${c}`}>{children}</span>}
export function Button({children,...props}:ButtonHTMLAttributes<HTMLButtonElement>){return <button {...props} className={`rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50 ${props.className||''}`}>{children}</button>}
