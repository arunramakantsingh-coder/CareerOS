'use client';

import {useEffect,useState} from 'react';
import {CareerOSShell,Card,Badge} from '@/components/CareerOSShell';
import {apiClient} from '@/lib/api/client';
import {useTheme, type CareerOSTheme} from '@/contexts/ThemeContext';

const themeOptions: Array<{key:CareerOSTheme; title:string; description:string}> = [
  {key:'light',title:'Light',description:'Professional career workspace'},
  {key:'dark',title:'Dark',description:'Premium modern AI workspace'},
  {key:'techno',title:'Techno',description:'Intelligence command center'},
];

export default function Settings(){
  const [me,setMe]=useState<any>();
  const [health,setHealth]=useState<any>();
  const [msg,setMsg]=useState('');
  const {theme,setTheme}=useTheme();

  useEffect(()=>{Promise.all([apiClient.me(),apiClient.healthCheck()]).then(([u,h])=>{setMe(u);setHealth(h)}).catch(e=>setMsg(e.message))},[]);

  return <CareerOSShell>
    <header className="mb-6 flex flex-col gap-2 border-b pb-6">
      <p className="text-xs font-semibold uppercase tracking-[.16em] text-primary">System</p>
      <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Settings</h1>
      <p className="max-w-3xl text-sm text-muted-foreground">Control your CareerOS experience, identity and workspace preferences.</p>
    </header>

    <div className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
      <Card title="Appearance" className="techno-glow">
        <div className="grid gap-3 md:grid-cols-3">
          {themeOptions.map(option=><button key={option.key} type="button" onClick={()=>setTheme(option.key)} className={`relative min-h-28 rounded-xl border p-4 text-left transition ${theme===option.key?'border-primary bg-primary/10 shadow-[0_0_24px_hsl(var(--primary)/.10)]':'bg-background/40 hover:border-primary/40 hover:bg-muted/40'}`}>
            {theme===option.key&&<span className="absolute right-3 top-3 rounded-full bg-primary/15 px-2 py-1 text-[10px] font-bold text-primary">Active</span>}
            <span className="block text-sm font-semibold">{option.title}</span>
            <span className="mt-2 block text-xs leading-5 text-muted-foreground">{option.description}</span>
          </button>)}
        </div>
        <p className="mt-4 text-xs text-muted-foreground">Your selection is stored locally and persists across navigation and browser refresh.</p>
      </Card>

      <Card title="Current session">
        <div className="space-y-5">
          <div><p className="text-xs text-muted-foreground">Identity</p><p className="mt-1 font-medium">{me?.name||me?.email||'—'}</p></div>
          <div><p className="text-xs text-muted-foreground">Tenant</p><p className="mt-1 font-mono text-sm">{me?.tenant_id||'—'}</p></div>
          <div><p className="text-xs text-muted-foreground">Authentication</p><div className="mt-1"><Badge tone="good">Authenticated</Badge></div></div>
        </div>
      </Card>
    </div>

    <div className="mt-4 grid gap-4 md:grid-cols-3">
      <Card title="API health"><p className="text-sm text-muted-foreground">Backend: <strong className="text-primary">{health?.status||'checking…'}</strong></p></Card>
      <Card title="Security & access"><p className="text-sm text-muted-foreground">Existing JWT authentication remains the session boundary for CareerOS.</p></Card>
      <Card title="Evidence-first privacy"><p className="text-sm text-muted-foreground">Professional claims should remain traceable to the evidence that produced them.</p></Card>
    </div>

    {msg&&<p className="mt-4 text-sm text-red-600">{msg}</p>}
  </CareerOSShell>
}
