'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { CareerOSShell, PageHeader, Card, Badge, Button } from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';

type ProviderHealth = {
  status?: string;
  reachable?: boolean;
  checked_at?: string | null;
  last_latency_ms?: number | null;
  avg_latency_ms?: number | null;
  p50_latency_ms?: number | null;
  p95_latency_ms?: number | null;
  checks?: number;
  successful_checks?: number;
  failed_checks?: number;
  consecutive_failures?: number;
  last_error?: string | null;
  quota?: Record<string, string | number>;
};

type Provider = {
  provider: string;
  label: string;
  category: string;
  model?: string;
  base_url?: string;
  configured: boolean;
  active: boolean;
  control_state?: string;
  deactivated?: boolean;
  priority: number;
  capabilities?: string[];
  api_key_present?: boolean;
  api_key_last4?: string | null;
  last_tested_at?: string | null;
  last_test_status?: string | null;
  last_error?: string | null;
  routing_policy?: any;
  telemetry?: any;
  health?: ProviderHealth;
  health_fresh?: boolean;
};

type Observability = { routing?: any; usage?: any; providers?: Provider[] };
type HealthPolicy = { enabled: boolean; interval_seconds: number; grace_seconds: number; health_ttl_seconds: number };

const PROVIDER_CATALOG: Provider[] = [
  { provider: 'ollama', label: 'Ollama', category: 'local', model: 'gemma3:4b', base_url: 'http://host.docker.internal:11434', configured: false, active: false, priority: 100, capabilities: ['local', 'private', 'structured_output'] },
  { provider: 'openrouter', label: 'OpenRouter', category: 'cloud', model: 'openrouter/free', base_url: 'https://openrouter.ai/api/v1', configured: false, active: false, priority: 100, capabilities: ['routing', 'model_choice', 'structured_output'] },
  { provider: 'openai', label: 'OpenAI', category: 'cloud', model: 'gpt-5.6-luna', base_url: 'https://api.openai.com/v1', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'structured_output', 'vision'] },
  { provider: 'gemini', label: 'Google Gemini', category: 'cloud', model: 'gemini-3.5-flash-lite', base_url: '', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'structured_output', 'long_context'] },
  { provider: 'anthropic', label: 'Anthropic Claude', category: 'cloud', model: 'claude-sonnet-5', base_url: 'https://api.anthropic.com', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'long_context', 'structured_output'] },
  { provider: 'mistral', label: 'Mistral AI', category: 'cloud', model: 'mistral-large-latest', base_url: 'https://api.mistral.ai/v1', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'structured_output', 'document_intelligence'] },
  { provider: 'xai', label: 'xAI', category: 'cloud', model: 'grok-4.6', base_url: 'https://api.x.ai/v1', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'vision', 'web_search'] },
  { provider: 'groq', label: 'Groq', category: 'cloud', model: 'llama-4-scout-17b-16e-instruct', base_url: 'https://api.groq.com/openai/v1', configured: false, active: false, priority: 100, capabilities: ['fast', 'structured_output'] },
  { provider: 'deepseek', label: 'DeepSeek', category: 'cloud', model: 'deepseek-v4-pro', base_url: 'https://api.deepseek.com', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'coding', 'structured_output', 'long_context'] },
];

const TASKS: [string, string, string[]][] = [
  ['cv_extraction', 'CV extraction', ['structured_output']],
  ['profile_reconciliation', 'Profile reconciliation', ['structured_output', 'reasoning']],
  ['document_classification', 'Document classification', ['structured_output']],
  ['persona_generation', 'Persona generation', ['reasoning']],
  ['jd_analysis', 'JD analysis', ['reasoning', 'long_context']],
  ['matching', 'Matching', ['reasoning', 'structured_output']],
  ['research', 'Research', ['long_context']],
  ['interview_intelligence', 'Interview intelligence', ['reasoning']],
  ['embedding', 'Embedding', ['embedding']],
  ['bulk_processing', 'Bulk processing', ['fast', 'structured_output']],
];

const HEALTH_INTERVALS = [300, 600, 900, 1800, 3600, 7200, 21600];

function healthTone(p: Provider, fresh: boolean) {
  if (p.health?.status === 'healthy' && fresh) return 'good';
  if (p.health?.status === 'unhealthy') return 'warn';
  if (p.health?.status === 'healthy') return 'blue';
  return p.configured ? 'blue' : 'muted';
}
function healthLabel(p: Provider, fresh: boolean) {
  if (p.health?.status === 'healthy' && fresh) return 'Healthy';
  if (p.health?.status === 'healthy') return 'Stale';
  if (p.health?.status === 'unhealthy') return 'Unhealthy';
  return p.configured ? 'Health check required' : 'Not configured';
}
function controlLabel(p: Provider) {
  if (!p.configured) return 'Not configured';
  if (p.active) return 'Active';
  return 'Deactivated';
}
function controlTone(p: Provider) {
  if (!p.configured) return 'muted';
  if (p.active) return 'good';
  return 'blue';
}
function fmtTime(v?: string | null) { return v ? new Date(v).toLocaleString() : 'Not checked'; }
function fmtMs(v?: number | null) { return v == null ? '—' : `${Number(v).toFixed(1)} ms`; }
function fmtInterval(seconds: number) { if (seconds % 3600 === 0) return `${seconds / 3600} hour${seconds === 3600 ? '' : 's'}`; if (seconds % 60 === 0) return `${seconds / 60} minutes`; return `${seconds} seconds`; }

export default function IntelligenceEngine() {
  const [providers, setProviders] = useState<Provider[]>(PROVIDER_CATALOG);
  const [activeProvider, setActiveProvider] = useState('');
  const [selected, setSelected] = useState('ollama');
  const [form, setForm] = useState({ model: '', base_url: '', api_key: '', priority: 100 });
  const [busy, setBusy] = useState('');
  const [message, setMessage] = useState('');
  const [registryError, setRegistryError] = useState('');
  const [gatewayError, setGatewayError] = useState('');
  const [healthError, setHealthError] = useState('');
  const [observabilityError, setObservabilityError] = useState('');
  const [status, setStatus] = useState<any>(null);
  const [obs, setObs] = useState<Observability | null>(null);
  const [healthPolicy, setHealthPolicy] = useState<HealthPolicy>({ enabled: true, interval_seconds: 900, grace_seconds: 60, health_ttl_seconds: 960 });
  const [dailyLimit, setDailyLimit] = useState('');
  const loadingRef = useRef(false);

  const current = useMemo(() => providers.find((p) => p.provider === selected), [providers, selected]);
  const usage = obs?.usage || {};
  const activeProviders = providers.filter((p) => p.active && p.configured);
  const currentHealthy = Boolean(current?.health?.status === 'healthy' && current.health_fresh);
  const configuredCount = providers.filter((p) => p.configured).length;
  const healthyCount = providers.filter((p) => p.configured && p.health?.status === 'healthy' && p.health_fresh).length;
  const lastHealthCheck = providers.map((p) => p.health?.checked_at).filter(Boolean).sort().at(-1);

  const mergeProviders = (remote: Provider[], healthData?: any) => {
    const remoteMap = new Map(remote.map((p) => [p.provider, p]));
    const healthMap = new Map((healthData?.providers || []).map((p: any) => [p.provider, p]));
    return PROVIDER_CATALOG.map((fallback) => {
      const live = remoteMap.get(fallback.provider);
      const h: any = healthMap.get(fallback.provider);
      return {
        ...fallback,
        ...(live || {}),
        health: h?.health || live?.health || fallback.health,
        health_fresh: h ? Boolean(h.health_fresh) : Boolean(live?.health_fresh),
      };
    });
  };

  const applySelected = (list: Provider[]) => {
    const p = list.find((x) => x.provider === selected) || list[0];
    if (!p) return;
    if (p.provider !== selected) setSelected(p.provider);
    setForm({ model: p.model || '', base_url: p.base_url || '', api_key: '', priority: p.priority || 100 });
    setDailyLimit(p.routing_policy?.daily_request_limit ? String(p.routing_policy.daily_request_limit) : '');
  };

  const load = async () => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    setRegistryError('');
    const results = await Promise.allSettled([
      apiClient.intelligenceProviders(),
      apiClient.get('/api/v1/intelligence/status'),
      apiClient.intelligenceObservability(),
      apiClient.intelligenceProviderHealth(),
      apiClient.intelligenceProviderHealthPolicy(),
    ]);
    const [registryResult, statusResult, obsResult, healthResult, policyResult] = results;
    if (registryResult.status === 'fulfilled') {
      const data = registryResult.value;
      const remote = Array.isArray(data.providers) ? data.providers : [];
      const base = mergeProviders(remote);
      setProviders(base);
      applySelected(base);
      setActiveProvider(data.active_provider || '');
    } else setRegistryError(registryResult.reason?.message || 'Unable to load provider registry.');
    if (statusResult.status === 'fulfilled') { setStatus(statusResult.value); setGatewayError(''); }
    else { setStatus(null); setGatewayError('Gateway status unavailable.'); }
    if (obsResult.status === 'fulfilled') { setObs(obsResult.value); setObservabilityError(''); }
    else { setObservabilityError('Usage and routing telemetry unavailable.'); }
    if (healthResult.status === 'fulfilled') {
      const data = healthResult.value;
      setHealthError('');
      if (data.health_policy) setHealthPolicy((p) => ({ ...p, ...data.health_policy, health_ttl_seconds: data.health_ttl_seconds || p.health_ttl_seconds }));
      setProviders((previous) => mergeProviders(previous, data));
    } else setHealthError('Health data unavailable.');
    if (policyResult.status === 'fulfilled') setHealthPolicy(policyResult.value);
    loadingRef.current = false;
  };

  useEffect(() => { void load(); }, []);
  useEffect(() => {
    const timer = window.setInterval(() => void load(), 15000);
    return () => window.clearInterval(timer);
  }, []);

  const selectProvider = (name: string) => {
    const p = providers.find((x) => x.provider === name) || PROVIDER_CATALOG.find((x) => x.provider === name);
    if (!p) return;
    setSelected(name);
    setForm({ model: p.model || '', base_url: p.base_url || '', api_key: '', priority: p.priority || 100 });
    setDailyLimit(p.routing_policy?.daily_request_limit ? String(p.routing_policy.daily_request_limit) : '');
    setMessage('');
  };

  const save = async () => {
    setBusy('save'); setMessage('');
    try {
      await apiClient.saveIntelligenceProvider({ provider: selected, model: form.model || undefined, base_url: form.base_url || undefined, api_key: form.api_key || undefined, priority: form.priority });
      setForm((f) => ({ ...f, api_key: '' })); await load();
      setMessage(`${current?.label || selected} configuration saved. Activation remains a separate operator action.`);
    } catch (e: any) { setMessage(e.message || 'Unable to save provider'); }
    finally { setBusy(''); }
  };

  const test = async () => {
    setBusy('test'); setMessage('');
    try {
      const result = await apiClient.testIntelligenceProvider({ provider: selected, model: form.model || undefined, base_url: form.base_url || undefined, api_key: form.api_key || undefined });
      setForm((f) => ({ ...f, api_key: '' })); await load();
      setMessage(`Connection test passed: ${result.provider} / ${result.model}`);
    } catch (e: any) { setMessage(e.message || 'Provider test failed'); }
    finally { setBusy(''); }
  };

  const healthCheck = async (all = false) => {
    setBusy(all ? 'health-all' : 'health'); setMessage('');
    try {
      const result = await apiClient.runIntelligenceProviderHealthCheck(all ? {} : { provider: selected, model: form.model || undefined, base_url: form.base_url || undefined, api_key: form.api_key || undefined });
      setForm((f) => ({ ...f, api_key: '' })); await load();
      const ok = (result.providers || []).filter((p: any) => p.health?.status === 'healthy').length;
      setMessage(all ? `Health check completed: ${ok}/${result.providers?.length || 0} configured providers healthy.` : `Health check completed for ${current?.label || selected}: ${result.providers?.[0]?.health?.status || 'unknown'}.`);
    } catch (e: any) { setMessage(e.message || 'Provider health check failed'); }
    finally { setBusy(''); }
  };

  const activate = async () => {
    setBusy('activate'); setMessage('');
    try {
      const result = await apiClient.activateIntelligenceProvider(selected); await load(); setActiveProvider(result.active_provider || selected);
      setMessage(`${current?.label || selected} activated. Multiple providers may be active; runtime ranking will decide which eligible provider runs each task.`);
    } catch (e: any) { setMessage(e.message || 'Unable to activate provider'); }
    finally { setBusy(''); }
  };

  const deactivate = async () => {
    setBusy('deactivate'); setMessage('');
    try {
      await apiClient.deactivateIntelligenceProvider(selected); await load();
      setMessage(`${current?.label || selected} manually deactivated. It remains configured but is excluded from runtime routing.`);
    } catch (e: any) { setMessage(e.message || 'Unable to deactivate provider'); }
    finally { setBusy(''); }
  };

  const savePolicy = async () => {
    setBusy('policy'); setMessage('');
    try {
      await apiClient.updateIntelligenceRoutingPolicy({ provider: selected, fallback_enabled: true, daily_request_limit: dailyLimit ? Number(dailyLimit) : null });
      await load(); setMessage(`Runtime policy updated for ${current?.label || selected}.`);
    } catch (e: any) { setMessage(e.message || 'Unable to update runtime policy'); }
    finally { setBusy(''); }
  };

  const saveHealthPolicy = async () => {
    setBusy('health-policy'); setMessage('');
    try {
      const result = await apiClient.updateIntelligenceProviderHealthPolicy(healthPolicy);
      setHealthPolicy(result); await load();
      setMessage(`Automatic health checks ${result.enabled ? 'enabled' : 'disabled'} at ${fmtInterval(result.interval_seconds)} intervals.`);
    } catch (e: any) { setMessage(e.message || 'Unable to update automatic health policy'); }
    finally { setBusy(''); }
  };

  const eligibleForTask = (requirements: string[]) => providers.filter((p) => p.active && p.configured && p.health_fresh && requirements.every((r) => (p.capabilities || []).includes(r))).map((p) => p.provider);

  return (
    <CareerOSShell>
      <PageHeader
        eyebrow="Project Control · Global Intelligence"
        title="Global Intelligence Engine"
        description="Central control plane for provider configuration, health, task routing, fallback and runtime eligibility across CareerOS."
        action={<Badge tone={status?.status === 'ready' ? 'good' : 'warn'}>{status?.status === 'ready' ? 'Gateway ready' : status?.status || 'Checking'}</Badge>}
      />

      {registryError && <div className="mb-3 rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm">{registryError}</div>}
      {message && <div className="mb-5 rounded-xl border bg-card px-4 py-3 text-sm">{message}</div>}

      <Card className="mb-5" title="Global Intelligence control plane">
        <div className="overflow-x-auto rounded-xl border bg-muted/10 p-4">
          <div className="min-w-[760px] text-center font-mono text-xs">
            <div className="mx-auto w-fit rounded-xl border px-6 py-2 font-semibold">GLOBAL INTELLIGENCE ENGINE</div>
            <div className="mx-auto h-5 w-px border-l" />
            <div className="grid grid-cols-2 gap-8">
              <div className="rounded-xl border p-3"><p className="font-semibold">PROVIDER CONTROL</p><div className="mt-2 text-muted-foreground">Registry · Credentials · Activate / Deactivate</div></div>
              <div className="rounded-xl border p-3"><p className="font-semibold">RUNTIME CONTROL</p><div className="mt-2 text-muted-foreground">Task Routing · Ranking · Fallback</div></div>
            </div>
            <div className="mx-auto h-5 w-px border-l" />
            <div className="mx-auto w-fit rounded-xl border px-8 py-2 font-semibold">HEALTH GATE</div>
            <div className="mx-auto h-5 w-px border-l" />
            <div className="grid grid-cols-2 gap-8"><div className="rounded-xl border p-2">Health / Latency</div><div className="rounded-xl border p-2">Quota / Rate limits</div></div>
            <div className="mx-auto h-5 w-px border-l" />
            <div className="mx-auto w-fit rounded-xl border px-8 py-2 font-semibold">AI GATEWAY</div>
            <div className="mx-auto h-5 w-px border-l" />
            <div className="flex justify-center gap-2 text-[10px]">{PROVIDER_CATALOG.map((p) => <span key={p.provider} className="rounded-lg border px-2 py-1">{p.label}</span>)}</div>
          </div>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-5">
        <Card><p className="text-xs text-muted-foreground">Active providers</p><p className="mt-2 font-semibold">{activeProviders.length}</p><p className="mt-1 text-[11px] text-muted-foreground">{activeProviders.map((p) => p.label).join(', ') || 'None'}</p></Card>
        <Card><p className="text-xs text-muted-foreground">Configured</p><p className="mt-2 font-semibold">{configuredCount}</p></Card>
        <Card><p className="text-xs text-muted-foreground">Healthy & fresh</p><p className="mt-2 font-semibold">{healthyCount}</p></Card>
        <Card><p className="text-xs text-muted-foreground">Gateway</p><p className="mt-2 font-semibold">{gatewayError ? 'Unavailable' : status?.status || 'Checking…'}</p></Card>
        <Card><p className="text-xs text-muted-foreground">Fallback requests</p><p className="mt-2 font-semibold">{usage.fallback_requests ?? 0}</p></Card>
      </div>

      <Card className="mt-5" title="Automatic provider health checks">
        <div className="rounded-xl border bg-muted/20 p-3 text-xs leading-5 text-muted-foreground">Health checks are non-generative control-plane checks. The backend scheduler runs independently of this browser page. Health freshness follows the configured interval plus the grace period.</div>
        <div className="mt-4 grid gap-4 md:grid-cols-4">
          <label className="flex items-center gap-3 rounded-xl border p-3"><input type="checkbox" checked={healthPolicy.enabled} onChange={(e) => setHealthPolicy((p) => ({ ...p, enabled: e.target.checked }))} /><span><span className="block text-sm font-semibold">Automatic checks</span><span className="text-xs text-muted-foreground">Backend scheduler</span></span></label>
          <label><span className="text-xs font-medium">Check interval</span><select value={healthPolicy.interval_seconds} onChange={(e) => setHealthPolicy((p) => ({ ...p, interval_seconds: Number(e.target.value) }))} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm">{HEALTH_INTERVALS.map((s) => <option key={s} value={s}>{fmtInterval(s)}</option>)}</select></label>
          <div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Last check</p><p className="mt-1 text-sm font-semibold">{fmtTime(lastHealthCheck)}</p></div>
          <div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Freshness TTL</p><p className="mt-1 text-sm font-semibold">{fmtInterval(healthPolicy.health_ttl_seconds)}</p></div>
        </div>
        <div className="mt-4 flex flex-wrap gap-2"><Button onClick={saveHealthPolicy} disabled={!!busy}>{busy === 'health-policy' ? 'Saving…' : 'Save Health Policy'}</Button><Button onClick={() => healthCheck(true)} disabled={!!busy}>{busy === 'health-all' ? 'Checking all…' : 'Run Health Check Now'}</Button><span className="self-center text-xs text-muted-foreground">Configured interval: {fmtInterval(healthPolicy.interval_seconds)}</span></div>
      </Card>

      <Card className="mt-5" title="Provider registry">
        <p className="mb-4 text-sm text-muted-foreground">Control state and operational health are deliberately separate. A provider can be configured but deactivated, or active but temporarily stale/unhealthy.</p>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {providers.map((p) => {
            const fresh = Boolean(p.health_fresh);
            return <button key={p.provider} type="button" onClick={() => selectProvider(p.provider)} className={`rounded-2xl border p-4 text-left transition ${selected === p.provider ? 'border-primary bg-primary/5 shadow-sm' : 'hover:bg-muted/40'}`}>
              <div className="flex items-start justify-between gap-3"><div><p className="font-semibold">{p.label}</p><p className="mt-1 text-[11px] uppercase tracking-[.12em] text-muted-foreground">{p.category}</p></div><div className="flex flex-wrap justify-end gap-1"><Badge tone={controlTone(p) as any}>{controlLabel(p)}</Badge><Badge tone={healthTone(p, fresh) as any}>{healthLabel(p, fresh)}</Badge></div></div>
              <p className="mt-3 text-xs text-muted-foreground">{p.model || 'Model not selected'}</p>
              <p className="mt-1 text-[11px] text-muted-foreground">{p.api_key_present ? `Key saved ••••${p.api_key_last4}` : p.configured ? 'Configured credentials' : 'No credentials configured'}</p>
              <div className="mt-3 flex flex-wrap gap-1">{(p.capabilities || []).slice(0, 5).map((x) => <Badge key={x}>{x}</Badge>)}</div>
              <p className="mt-3 text-[11px] text-muted-foreground">Health checked: {fmtTime(p.health?.checked_at)}</p>
            </button>;
          })}
        </div>
      </Card>

      {current && <Card className="mt-5" title={`${current.label} provider configuration`}>
        <div className="rounded-xl border bg-muted/20 p-3 text-xs leading-5 text-muted-foreground">Save, Test, Health, Activate and Deactivate are separate operator actions. Activation never happens merely because credentials were saved. Runtime routing only considers providers that are active, compatible with the task and health-fresh.</div>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <div><label className="text-xs font-medium">Model</label><input value={form.model} onChange={(e) => setForm((f) => ({ ...f, model: e.target.value }))} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div>
          <div><label className="text-xs font-medium">Manual priority</label><input type="number" min={1} max={1000} value={form.priority} onChange={(e) => setForm((f) => ({ ...f, priority: Number(e.target.value) || 100 }))} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /><p className="mt-1 text-[11px] text-muted-foreground">Final deterministic tie-breaker after task compatibility, health reliability and latency. It does not override health.</p></div>
          {selected !== 'gemini' && <div><label className="text-xs font-medium">Base URL</label><input value={form.base_url} onChange={(e) => setForm((f) => ({ ...f, base_url: e.target.value }))} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div>}
          {selected !== 'ollama' && <div><label className="text-xs font-medium">API key</label><input type="password" value={form.api_key} onChange={(e) => setForm((f) => ({ ...f, api_key: e.target.value }))} placeholder={current.api_key_present ? 'Saved — enter only to replace' : 'Enter API key'} autoComplete="new-password" className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div>}
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button onClick={save} disabled={!!busy}>{busy === 'save' ? 'Saving…' : 'Save Credentials'}</Button>
          <Button onClick={test} disabled={!!busy}>{busy === 'test' ? 'Testing…' : 'Test Connection'}</Button>
          <Button onClick={() => healthCheck(false)} disabled={!!busy}>{busy === 'health' ? 'Checking…' : 'Run Health Check'}</Button>
          {current.active ? <Button onClick={deactivate} disabled={!!busy}>{busy === 'deactivate' ? 'Deactivating…' : 'Deactivate Provider'}</Button> : <Button onClick={activate} disabled={!!busy || !current.configured || !currentHealthy}>{busy === 'activate' ? 'Activating…' : current.configured ? currentHealthy ? 'Activate Provider' : 'Health Check Required' : 'Configure Provider First'}</Button>}
        </div>
        <p className="mt-3 text-xs text-muted-foreground">Manual deactivation excludes this provider from runtime selection while preserving its credentials and health history.</p>
      </Card>}

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <Card title="Task-based routing">
          <p className="text-sm text-muted-foreground">For every task: active → configured → task-compatible → health-fresh → ranked by health reliability, latency and then manual priority. A provider that lacks a task capability is skipped, not a failure.</p>
          <div className="mt-4 space-y-2">{TASKS.map(([key, label, requirements]) => { const eligible = eligibleForTask(requirements); return <div key={key} className="rounded-xl border px-3 py-3"><div className="flex items-center justify-between gap-3"><span className="text-sm font-medium">{label}</span><span className="text-[11px] text-muted-foreground">{eligible.length ? eligible.join(' → ') : 'No eligible provider'}</span></div><div className="mt-2 flex flex-wrap gap-1">{requirements.map((r) => <Badge key={r}>{r}</Badge>)}</div></div>; })}</div>
          {observabilityError ? <p className="mt-4 text-xs text-muted-foreground">{observabilityError}</p> : <div className="mt-4 rounded-xl border p-3 text-xs text-muted-foreground">Runtime healthy order: {(obs?.routing?.healthy_provider_order || []).join(' → ') || 'No healthy active provider yet'}</div>}
        </Card>

        <Card title="Fallback routing">
          <p className="text-sm text-muted-foreground">Fallback stays inside the active + compatible + recently healthy pool. A failed generation is recorded before the next eligible provider is attempted.</p>
          <div className="mt-4 rounded-xl border p-4 space-y-3 text-sm">
            <div className="flex justify-between gap-4"><span>Primary active provider</span><strong>{activeProvider || '—'}</strong></div>
            <div className="flex justify-between gap-4"><span>Active providers</span><span className="text-xs text-muted-foreground">{(obs?.routing?.active_provider_order || activeProviders.map((p) => p.provider)).join(' → ') || '—'}</span></div>
            <div className="flex justify-between gap-4"><span>Healthy eligible order</span><span className="text-xs text-muted-foreground">{(obs?.routing?.healthy_provider_order || []).join(' → ') || '—'}</span></div>
            <div className="flex justify-between"><span>Fallback</span><Badge tone={obs?.routing?.fallback_enabled ? 'good' : 'warn'}>{obs?.routing?.fallback_enabled ? 'Enabled' : 'Disabled'}</Badge></div>
            <div className="flex justify-between"><span>Fallback requests</span><strong>{usage.fallback_requests ?? 0}</strong></div>
          </div>
        </Card>

        <Card title="Health / latency / quota">
          <p className="text-sm text-muted-foreground">Operational health is separate from generation telemetry. Quota/rate-limit signals are displayed only when the provider supplies them.</p>
          <div className="mt-4 overflow-x-auto"><table className="w-full text-left text-xs"><thead><tr className="border-b"><th className="px-2 py-2">Provider</th><th className="px-2 py-2">Control</th><th className="px-2 py-2">Health</th><th className="px-2 py-2">Avg</th><th className="px-2 py-2">P95</th><th className="px-2 py-2">Failures</th><th className="px-2 py-2">Quota</th></tr></thead><tbody>{providers.map((p) => { const t = p.health || {}; const fresh = Boolean(p.health_fresh); const quota = t.quota && Object.keys(t.quota).length ? JSON.stringify(t.quota) : 'Not reported'; return <tr key={p.provider} className="border-b last:border-0"><td className="px-2 py-2 font-medium">{p.label}</td><td className="px-2 py-2"><Badge tone={controlTone(p) as any}>{controlLabel(p)}</Badge></td><td className="px-2 py-2"><Badge tone={healthTone(p, fresh) as any}>{healthLabel(p, fresh)}</Badge><div className="mt-1 text-[10px] text-muted-foreground">{fmtTime(t.checked_at)}</div></td><td className="px-2 py-2">{fmtMs(t.avg_latency_ms)}</td><td className="px-2 py-2">{fmtMs(t.p95_latency_ms)}</td><td className="px-2 py-2">{t.failed_checks || 0}{t.consecutive_failures ? ` (${t.consecutive_failures} consecutive)` : ''}</td><td className="max-w-56 truncate px-2 py-2" title={quota}>{quota}</td></tr>; })}</tbody></table></div>
          {healthError && <p className="mt-3 text-xs text-muted-foreground">{healthError}</p>}
          <p className="mt-3 text-[11px] text-muted-foreground">Freshness window: {fmtInterval(healthPolicy.health_ttl_seconds)} · automatic interval: {fmtInterval(healthPolicy.interval_seconds)}.</p>
        </Card>

        <Card title="Usage & cost controls">
          <p className="text-sm text-muted-foreground">Generation telemetry is recorded at the AI boundary. Daily request limits are enforced before generation.</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3"><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Requests</p><p className="mt-1 text-lg font-semibold">{usage.requests ?? 0}</p></div><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Tokens reported</p><p className="mt-1 text-lg font-semibold">{usage.total_tokens ?? 0}</p></div><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Estimated cost</p><p className="mt-1 text-lg font-semibold">{providers.some((p) => p.telemetry?.estimated_cost !== undefined) ? `$${providers.reduce((n, p) => n + Number(p.telemetry?.estimated_cost || 0), 0).toFixed(4)}` : 'Not reported'}</p></div></div>
          <div className="mt-4 flex flex-wrap items-end gap-3"><div className="min-w-48"><label className="text-xs font-medium">Daily request limit for {current?.label || selected}</label><input type="number" min={1} placeholder="No limit" value={dailyLimit} onChange={(e) => setDailyLimit(e.target.value)} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div><Button onClick={savePolicy} disabled={!!busy}>{busy === 'policy' ? 'Applying…' : 'Apply usage policy'}</Button></div>
        </Card>
      </div>

      <Card className="mt-5" title="Architecture boundary">
        <div className="space-y-3 text-sm leading-6 text-muted-foreground">
          <p><strong className="text-foreground">Provider state:</strong> configured, active and manually deactivated are control states. Healthy, stale and unhealthy are operational health states. They are never collapsed into one badge.</p>
          <p><strong className="text-foreground">Runtime ranking:</strong> task capability is a hard eligibility gate. Health freshness is a hard gate. Among eligible active providers, reliability and latency drive ranking; manual priority is the final deterministic tie-breaker.</p>
          <p><strong className="text-foreground">Fallback:</strong> when a generation fails, the runtime records the failure and tries the next eligible provider. A provider that cannot perform the requested task does not stop the workflow.</p>
          <p><strong className="text-foreground">AI is not the system of record:</strong> AI produces candidate facts and recommendations. CareerOS services remain authoritative for validation, persistence, provenance, permissions and state transitions.</p>
        </div>
      </Card>
    </CareerOSShell>
  );
}
