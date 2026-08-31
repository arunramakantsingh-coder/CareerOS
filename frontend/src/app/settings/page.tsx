'use client';

import {useEffect,useState} from 'react';
import {CareerOSShell,Card,Badge} from '@/components/CareerOSShell';
import {apiClient} from '@/lib/api/client';
import {useTheme, type CareerOSTheme} from '@/contexts/ThemeContext';

const themeOptions: Array<{key:CareerOSTheme; title:string; description:string}> = [
  {key:'light',title:'Light',description:'Bright professional workspace'},
  {key:'dark',title:'Dark',description:'Low-light modern career workspace'},
  {key:'techno',title:'Command',description:'Translucent career intelligence operating-system mode'},
];

export default function Settings(){
  const [me,setMe]=useState<any>(); const [health,setHealth]=useState<any>(); const [msg,setMsg]=useState(''); const [section,setSection]=useState('appearance');
  const {theme,setTheme}=useTheme();
  useEffect(()=>{Promise.all([apiClient.me(),apiClient.healthCheck()]).then(([u,h])=>{setMe(u);setHealth(h)}).catch(e=>setMsg(e.message))},[]);

  const menu=[['appearance','Appearance'],['account','Account & session'],['connections','Connections'],['privacy','Privacy & evidence'],['system','System health']];
  return <CareerOSShell>
    <header className="mb-6 border-b pb-6"><p className="text-xs font-semibold uppercase tracking-[.16em] text-primary">Application</p><h1 className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">Settings</h1><p className="mt-2 max-w-3xl text-sm text-muted-foreground">Application-wide appearance, access, connections and workspace behavior. Career profile data is managed under Profile.</p></header>
    <div className="grid gap-5 lg:grid-cols-[240px_minmax(0,1fr)]">
      <aside className="h-fit rounded-xl border bg-card p-2">{menu.map(([key,label])=><button key={key} onClick={()=>setSection(key)} className={`w-full rounded-lg px-3 py-2.5 text-left text-sm font-medium ${section===key?'bg-primary/10 text-primary':'text-muted-foreground hover:bg-muted hover:text-foreground'}`}>{label}</button>)}</aside>
      <div className="space-y-4">
        {section==='appearance'&&<Card title="Application appearance" className="techno-glow"><div className="grid gap-3 md:grid-cols-3">{themeOptions.map(option=><button key={option.key} type="button" onClick={()=>setTheme(option.key)} className={`relative min-h-32 rounded-xl border p-4 text-left transition ${theme===option.key?'border-primary bg-primary/10 shadow-[0_0_24px_hsl(var(--primary)/.10)]':'bg-background/40 hover:border-primary/40 hover:bg-muted/40'}`}>{theme===option.key&&<span className="absolute right-3 top-3 rounded-full bg-primary/15 px-2 py-1 text-[10px] font-bold text-primary">Active</span>}<span className="block text-base font-semibold">{option.title}</span><span className="mt-2 block text-xs leading-5 text-muted-foreground">{option.description}</span></button>)}</div><p className="mt-4 text-xs text-muted-foreground">This is an application setting and applies consistently across CareerOS pages.</p></Card>}
        {section==='account'&&<Card title="Account & current session"><div className="grid gap-5 md:grid-cols-3"><div><p className="text-xs text-muted-foreground">Identity</p><p className="mt-1 font-medium">{me?.name||me?.email||'—'}</p></div><div><p className="text-xs text-muted-foreground">Tenant</p><p className="mt-1 font-mono text-sm">{me?.tenant_id||'—'}</p></div><div><p className="text-xs text-muted-foreground">Authentication</p><div className="mt-1"><Badge tone="good">Authenticated</Badge></div></div></div></Card>}
        {section==='connections'&&<Card title="External connections"><p className="text-sm text-muted-foreground">Google, Gmail and LinkedIn connections belong to application authorization and identity linking. Profile Intelligence shows the professional information contributed by those connections.</p></Card>}
        {section==='privacy'&&<Card title="Privacy & evidence"><p className="text-sm text-muted-foreground">Professional claims should remain traceable to source evidence. OAuth authorization and profile evidence are separate concepts and should remain explicit.</p></Card>}
        {section==='system'&&<div className="grid gap-4 md:grid-cols-2"><Card title="API health"><p className="text-sm text-muted-foreground">Backend: <strong className="text-primary">{health?.status||'checking…'}</strong></p></Card><Card title="Security boundary"><p className="text-sm text-muted-foreground">JWT authentication remains the CareerOS session boundary.</p></Card></div>}
      </div>
    </div>
    {msg&&<p className="mt-4 text-sm text-red-500">{msg}</p>}
  </CareerOSShell>
}
