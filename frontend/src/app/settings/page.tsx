'use client';

import { useEffect, useState } from 'react';
import { CareerOSShell, Card, PageHeader, Badge } from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';
import { useTheme } from '@/contexts/ThemeContext';

export default function Settings() {
  const [me, setMe] = useState<any>();
  const [health, setHealth] = useState<any>();
  const [msg, setMsg] = useState('');
  const { theme, setTheme } = useTheme();

  useEffect(() => {
    Promise.all([apiClient.me(), apiClient.healthCheck()]).then(([u, h]) => { setMe(u); setHealth(h); }).catch((e) => setMsg(e.message));
  }, []);

  return <CareerOSShell>
    <PageHeader eyebrow="System" title="Settings" description="Control your CareerOS experience, identity and workspace preferences." />

    <div className="grid gap-4 lg:grid-cols-[1.4fr_.8fr]">
      <Card title="Appearance">
        <div className="grid gap-3 sm:grid-cols-3">
          {([
            ['light', 'Light', 'Professional career workspace'],
            ['dark', 'Dark', 'Premium AI workspace'],
            ['techno', 'Techno', 'Intelligence command center'],
          ] as const).map(([value, label, copy]) => <button key={value} onClick={() => setTheme(value)} className={`rounded-2xl border p-4 text-left transition ${theme === value ? 'border-primary bg-primary/5 ring-2 ring-primary/10' : 'hover:bg-muted'}`}>
            <div className="flex items-center justify-between"><span className="font-semibold">{label}</span>{theme === value && <Badge tone="blue">Active</Badge>}</div>
            <p className="mt-1 text-xs leading-5 text-muted-foreground">{copy}</p>
          </button>)}
        </div>
        <p className="mt-4 text-xs text-muted-foreground">Your selection is stored locally and persists across navigation and browser refresh.</p>
      </Card>

      <Card title="Current session">
        <div className="space-y-4"><div><p className="text-xs text-muted-foreground">Identity</p><p className="mt-1 font-semibold">{me?.name || me?.email || '—'}</p></div><div><p className="text-xs text-muted-foreground">Tenant</p><p className="mt-1 break-all font-mono text-xs">{me?.tenant_id || '—'}</p></div><div><p className="text-xs text-muted-foreground">Authentication</p><Badge tone="good">Authenticated</Badge></div></div>
      </Card>
    </div>

    <div className="mt-4 grid gap-4 md:grid-cols-3">
      <Card title="API health"><p className="text-sm text-muted-foreground">Backend: <strong>{health?.status || 'checking…'}</strong></p></Card>
      <Card title="Security & access"><p className="text-sm text-muted-foreground">Existing JWT authentication remains the session boundary for CareerOS.</p></Card>
      <Card title="Evidence-first privacy"><p className="text-sm text-muted-foreground">Professional claims should remain traceable to the evidence that produced them.</p></Card>
    </div>
    {msg && <p className="mt-4 text-sm text-red-600">{msg}</p>}
  </CareerOSShell>;
}
