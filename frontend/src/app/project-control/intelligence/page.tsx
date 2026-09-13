'use client';

import { useEffect, useMemo, useState } from 'react';
import { CareerOSShell, PageHeader, Card, Badge, Button } from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';

type Provider = {
  provider: string;
  label: string;
  category: string;
  model?: string;
  base_url?: string;
  configured: boolean;
  active: boolean;
  priority: number;
  capabilities?: string[];
  api_key_present?: boolean;
  api_key_last4?: string | null;
  last_tested_at?: string | null;
  last_test_status?: string | null;
  last_error?: string | null;
};

export default function IntelligenceEngine() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [activeProvider, setActiveProvider] = useState('');
  const [selected, setSelected] = useState('ollama');
  const [form, setForm] = useState({ model: '', base_url: '', api_key: '', priority: 100 });
  const [busy, setBusy] = useState('');
  const [message, setMessage] = useState('');
  const [status, setStatus] = useState<any>(null);

  const load = async () => {
    const [data, health] = await Promise.all([apiClient.intelligenceProviders(), apiClient.get('/api/v1/intelligence/status')]);
    setProviders(data.providers || []);
    setActiveProvider(data.active_provider || '');
    setStatus(health);
    const current = (data.providers || []).find((p: Provider) => p.provider === selected) || data.providers?.[0];
    if (current) {
      setSelected(current.provider);
      setForm({ model: current.model || '', base_url: current.base_url || '', api_key: '', priority: current.priority || 100 });
    }
  };

  useEffect(() => { load().catch((e: any) => setMessage(e.message || 'Unable to load Intelligence Engine')); }, []);

  const current = useMemo(() => providers.find(p => p.provider === selected), [providers, selected]);
  const selectProvider = (name: string) => {
    const p = providers.find(x => x.provider === name);
    if (!p) return;
    setSelected(name);
    setForm({ model: p.model || '', base_url: p.base_url || '', api_key: '', priority: p.priority || 100 });
    setMessage('');
  };

  const save = async () => {
    setBusy('save'); setMessage('');
    try {
      await apiClient.saveIntelligenceProvider({ provider: selected, model: form.model || undefined, base_url: form.base_url || undefined, api_key: form.api_key || undefined, priority: form.priority });
      setForm(f => ({ ...f, api_key: '' }));
      await load();
      setMessage(`${current?.label || selected} credentials/configuration saved. The provider was not activated.`);
    } catch (e: any) { setMessage(e.message || 'Unable to save provider'); } finally { setBusy(''); }
  };

  const test = async () => {
    setBusy('test'); setMessage('');
    try {
      const result = await apiClient.testIntelligenceProvider({ provider: selected, model: form.model || undefined, base_url: form.base_url || undefined, api_key: form.api_key || undefined });
      setForm(f => ({ ...f, api_key: '' }));
      await load();
      setMessage(`Connection test passed: ${result.provider} / ${result.model}`);
    } catch (e: any) { setMessage(e.message || 'Provider test failed'); } finally { setBusy(''); }
  };

  const activate = async (name = selected) => {
    setBusy(`activate:${name}`); setMessage('');
    try {
      const result = await apiClient.activateIntelligenceProvider(name);
      await load();
      setMessage(`${providers.find(p => p.provider === name)?.label || name} is now the global active AI provider.`);
      setActiveProvider(result.active_provider);
    } catch (e: any) { setMessage(e.message || 'Unable to activate provider'); } finally { setBusy(''); }
  };

  return <CareerOSShell>
    <PageHeader eyebrow="Project Control · Global Intelligence" title="Global Intelligence Engine" description="One provider-neutral AI gateway for every CareerOS intelligence workload. Provider credentials are platform configuration, not user profile data." action={<Badge tone={status?.status === 'ready' ? 'good' : 'warn'}>{status?.status === 'ready' ? 'Gateway ready' : status?.status || 'Checking'}</Badge>} />

    {message && <div className="mb-5 rounded-xl border bg-card px-4 py-3 text-sm">{message}</div>}

    <div className="grid gap-4 md:grid-cols-4">
      <Card><p className="text-xs text-muted-foreground">Global active provider</p><p className="mt-2 font-semibold">{activeProvider || 'Not selected'}</p></Card>
      <Card><p className="text-xs text-muted-foreground">Gateway</p><p className="mt-2 font-semibold">{status?.status || 'Checking…'}</p></Card>
      <Card><p className="text-xs text-muted-foreground">Supported providers</p><p className="mt-2 font-semibold">{providers.length}</p></Card>
      <Card><p className="text-xs text-muted-foreground">Scope</p><p className="mt-2 font-semibold">Platform-wide</p></Card>
    </div>

    <Card className="mt-5" title="Provider registry">
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {providers.map(p => <button key={p.provider} type="button" onClick={() => selectProvider(p.provider)} className={`rounded-2xl border p-4 text-left transition ${selected === p.provider ? 'border-primary bg-primary/5' : 'hover:bg-muted/40'}`}>
          <div className="flex items-center justify-between gap-3"><div><p className="font-semibold">{p.label}</p><p className="mt-1 text-[11px] uppercase tracking-[.12em] text-muted-foreground">{p.category}</p></div><Badge tone={p.active ? 'good' : p.configured ? 'blue' : 'muted'}>{p.active ? 'Active' : p.configured ? 'Configured' : 'Not configured'}</Badge></div>
          <p className="mt-3 text-xs text-muted-foreground">{p.model || 'Model not selected'}</p>
          {p.api_key_present && <p className="mt-1 text-[11px] text-muted-foreground">Key saved · ••••{p.api_key_last4}</p>}
          <div className="mt-3 flex flex-wrap gap-1">{(p.capabilities || []).slice(0, 4).map(x => <Badge key={x}>{x}</Badge>)}</div>
        </button>)}
      </div>
    </Card>

    {current && <Card className="mt-5" title={`${current.label} configuration`}>
      <div className="rounded-xl border bg-muted/20 p-3 text-xs leading-5 text-muted-foreground">Credentials are stored encrypted on the CareerOS platform. The API never returns the secret; the browser only sees whether a key exists and its last four characters. <strong>Save Credentials</strong> does not activate the provider.</div>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <div><label className="text-xs font-medium">Model</label><input value={form.model} onChange={e => setForm(f => ({ ...f, model: e.target.value }))} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div>
        <div><label className="text-xs font-medium">Priority</label><input type="number" min={1} max={1000} value={form.priority} onChange={e => setForm(f => ({ ...f, priority: Number(e.target.value) || 100 }))} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div>
        {selected !== 'gemini' && <div><label className="text-xs font-medium">Base URL</label><input value={form.base_url} onChange={e => setForm(f => ({ ...f, base_url: e.target.value }))} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div>}
        {selected !== 'ollama' && <div><label className="text-xs font-medium">API key</label><input type="password" value={form.api_key} onChange={e => setForm(f => ({ ...f, api_key: e.target.value }))} placeholder={current.api_key_present ? 'Saved — enter only to replace' : 'Enter API key'} autoComplete="new-password" className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div>}
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <Button onClick={save} disabled={!!busy}>{busy === 'save' ? 'Saving…' : 'Save Credentials'}</Button>
        <Button onClick={test} disabled={!!busy}>{busy === 'test' ? 'Testing…' : 'Test Connection'}</Button>
        <Button onClick={() => activate()} disabled={!!busy || current.active}>{busy === `activate:${selected}` ? 'Activating…' : current.active ? 'Currently Active' : 'Activate Provider'}</Button>
      </div>
      <p className="mt-3 text-xs text-muted-foreground">Switching providers later only requires selecting a configured provider and pressing Activate. The saved key is reused.</p>
    </Card>}

    <div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {['Task-based routing', 'Fallback routing', 'Usage & cost controls', 'Health / latency / quota'].map((x, i) => <Card key={x}><p className="font-semibold">{x}</p><p className="mt-2 text-xs leading-5 text-muted-foreground">{i === 0 ? 'Route CV, documents, personas, jobs, research and interview work through one gateway.' : 'Planned control surface; no fake behavior is exposed until the corresponding runtime capability exists.'}</p></Card>)}
    </div>

    <Card className="mt-5" title="Architecture boundary">
      <div className="space-y-2 text-sm leading-6 text-muted-foreground"><p><strong className="text-foreground">One gateway:</strong> CareerOS modules do not call individual AI vendors directly.</p><p><strong className="text-foreground">Global scope:</strong> the configured engine serves authorized CareerOS users; user career data remains tenant/user scoped.</p><p><strong className="text-foreground">AI is not the system of record:</strong> structured changes still pass through CareerOS application services, validation, provenance and human approval rules.</p></div>
    </Card>
  </CareerOSShell>;
}
