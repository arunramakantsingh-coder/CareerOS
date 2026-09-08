'use client';

import { useEffect, useState } from 'react';
import { CareerOSShell, PageHeader, Card, Badge } from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';

export default function IntelligenceEngine() {
  const [status, setStatus] = useState<any>(null);
  const [capabilities, setCapabilities] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      apiClient.get('/api/v1/intelligence/status'),
      apiClient.get('/api/v1/intelligence/capabilities'),
    ]).then(([s, c]) => { setStatus(s); setCapabilities(c); }).catch((e: any) => setError(e.message || 'Unable to reach the Intelligence Engine'));
  }, []);

  const ready = status?.status === 'ready';
  const configured = status?.model_configured;

  return <CareerOSShell>
    <PageHeader eyebrow="Project Control" title="Intelligence Engine" description="The reusable CareerOS reasoning layer. It will serve identity, document, search, research, opportunity, connection and interview intelligence through a provider-neutral gateway." action={<Badge tone={ready ? 'good' : configured ? 'blue' : 'warn'}>{ready ? 'Ready' : configured ? 'Configured' : 'Coming online'}</Badge>} />
    {error && <div className="mb-5 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-700 dark:text-amber-300">{error}</div>}
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card><p className="text-xs text-muted-foreground">Provider</p><p className="mt-2 font-semibold">{status?.provider || 'Ollama gateway'}</p></Card>
      <Card><p className="text-xs text-muted-foreground">Model</p><p className="mt-2 break-all font-semibold">{status?.model || 'Not selected yet'}</p></Card>
      <Card><p className="text-xs text-muted-foreground">Runtime</p><p className="mt-2 font-semibold">{status?.ollama_reachable ? 'Reachable' : 'Not reachable'}</p></Card>
      <Card><p className="text-xs text-muted-foreground">Configuration</p><p className="mt-2 font-semibold">{configured ? 'Model configured' : 'Hardware/model selection pending'}</p></Card>
    </div>
    <div className="mt-5 grid gap-5 lg:grid-cols-2">
      <Card title="Planned intelligence domains"><div className="flex flex-wrap gap-2">{['Identity Intelligence','Document Intelligence','Search Intelligence','Opportunity Intelligence','Organization Intelligence','Recruiter Intelligence','Research Intelligence','Interview Intelligence'].map(x => <Badge key={x} tone="blue">{x}</Badge>)}</div></Card>
      <Card title="Architecture boundary"><div className="space-y-2 text-sm leading-6 text-muted-foreground"><p>AI can retrieve, reason and recommend, but it does not become the system of record.</p><p>Structured changes must pass through validated CareerOS application services.</p><p>Evidence, trust state and provenance remain attached to findings.</p></div></Card>
    </div>
    {capabilities?.capabilities?.length ? <Card className="mt-5" title="Gateway capabilities"><div className="flex flex-wrap gap-2">{capabilities.capabilities.map((x:string) => <Badge key={x}>{x}</Badge>)}</div></Card> : null}
  </CareerOSShell>;
}
