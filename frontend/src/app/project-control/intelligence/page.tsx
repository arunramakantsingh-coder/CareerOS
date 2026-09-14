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

const PROVIDER_CATALOG: Provider[] = [
  { provider: 'ollama', label: 'Ollama', category: 'local', model: 'gemma3:4b', base_url: 'http://host.docker.internal:11434', configured: false, active: false, priority: 100, capabilities: ['local', 'private', 'structured_output'] },
  { provider: 'openrouter', label: 'OpenRouter', category: 'cloud', model: 'openrouter/free', base_url: 'https://openrouter.ai/api/v1', configured: false, active: false, priority: 100, capabilities: ['routing', 'model_choice', 'structured_output'] },
  { provider: 'openai', label: 'OpenAI', category: 'cloud', model: 'gpt-5.6-luna', base_url: 'https://api.openai.com/v1', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'structured_output', 'vision'] },
  { provider: 'gemini', label: 'Google Gemini', category: 'cloud', model: 'gemini-3.5-flash-lite', base_url: '', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'structured_output', 'long_context'] },
  { provider: 'anthropic', label: 'Anthropic Claude', category: 'cloud', model: 'claude-sonnet-5', base_url: 'https://api.anthropic.com', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'long_context', 'structured_output'] },
  { provider: 'mistral', label: 'Mistral AI', category: 'cloud', model: 'mistral-large-latest', base_url: 'https://api.mistral.ai/v1', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'structured_output', 'document_intelligence'] },
  { provider: 'xai', label: 'xAI', category: 'cloud', model: 'grok-4.6', base_url: 'https://api.x.ai/v1', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'vision', 'web_search'] },
  { provider: 'groq', label: 'Groq', category: 'cloud', model: 'llama-4-scout-17b-16-instruct', base_url: 'https://api.groq.com/openai/v1', configured: false, active: false, priority: 100, capabilities: ['fast', 'structured_output'] },
  { provider: 'deepseek', label: 'DeepSeek', category: 'cloud', model: 'deepseek-v4-pro', base_url: 'https://api.deepseek.com', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'coding', 'structured_output', 'long_context'] },
];

const tasks: [string, string][] = [
  ['cv_extraction', 'CV extraction'], ['profile_reconciliation', 'Profile reconciliation'], ['document_classification', 'Document classification'],
  ['persona_generation', 'Persona generation'], ['jd_analysis', 'JD analysis'], ['matching', 'Matching'], ['research', 'Research'],
  ['interview_intelligence', 'Interview intelligence'], ['embedding', 'Embedding'], ['bulk_processing', 'Bulk processing'],
];

function healthTone(p: Provider, fresh: boolean) {
  if (p.health?.status === 'healthy' && fresh) return 'good';
  if (p.health?.status === 'unhealthy') return 'warn';
  return p.configured ? 'blue' : 'muted';
}
function healthLabel(p: Provider, fresh: boolean) {
  if (p.health?.status === 'healthy' && fresh) return 'Healthy';
  if (p.health?.status === 'healthy') return 'Stale';
  if (p.health?.status === 'unhealthy') return 'Unhealthy';
  return p.configured ? 'Health check required' : 'Not configured';
}
function fmtTime(v?: string | null) { return v ? new Date(v).toLocaleString() : 'Not checked'; }
function fmtMs(v?: number | null) { return v == null ? '—' : `${v} ms`; }

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
  const [dailyLimit, setDailyLimit] = useState('');
  const [healthTtl, setHealthTtl] = useState(900);
  const loadingRef = useRef(false);

  const current = useMemo(() => providers.find((p) => p.provider === selected), [providers, selected]);
  const currentHealthy = Boolean(current?.health?.status === 'healthy' && current.health_fresh);
  const liveProviders = obs?.providers?.length ? obs.providers : providers;
  const usage = obs?.usage || {};
  const activeLive = liveProviders.find((p) => p.active);

  const mergeProviders = (remote: Provider[], healthData?: any) => {
    const remoteMap = new Map(remote.map((p) => [p.provider, p]));
    const healthMap = new Map((healthData?.providers || []).map((p: any) => [p.provider, p]));
    return PROVIDER_CATALOG.map((fallback) => {
      const live = remoteMap.get(fallback.provider);
      const h: any = healthMap.get(fallback.provider);
      return { ...fallback, ...(live || {}), health: h?.health || live?.health, health_fresh: Boolean(h?.health_fresh) };
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
    try {
      const data = await apiClient.intelligenceProviders();
      const remote = Array.isArray(data.providers) ? data.providers : [];
      setProviders((previous) => {
        const base = mergeProviders(remote);
        applySelected(base);
        return base;
      });
      setActiveProvider(data.active_provider || '');
    } catch (e: any) {
      setRegistryError(e?.message || 'Unable to load provider registry.');
    } finally {
      loadingRef.current = false;
    }

    const results = await Promise.allSettled([
      apiClient.get('/api/v1/intelligence/status'),
      apiClient.intelligenceObservability(),
      apiClient.intelligenceProviderHealth(),
    ]);
    const [statusResult, obsResult, healthResult] = results;
    if (statusResult.status === 'fulfilled') { setStatus(statusResult.value); setGatewayError(''); }
    else { setStatus(null); setGatewayError('Gateway status unavailable.'); }
    if (obsResult.status === 'fulfilled') { setObs(obsResult.value); setObservabilityError(''); }
    else { setObservabilityError('Usage and routing telemetry unavailable.'); }
    if (healthResult.status === 'fulfilled') {
      const healthData = healthResult.value;
      setHealthTtl(healthData.health_ttl_seconds || 900);
      setHealthError('');
      setProviders((previous) => mergeProviders(previous, healthData));
    } else { setHealthError('Health data unavailable. Run a health check when the API is reachable.'); }
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
      setMessage(`${current?.label || selected} credentials/configuration saved. The provider was not activated.`);
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
      setMessage(all ? `Health check completed: ${ok}/${result.providers?.length || 0} providers healthy.` : `Health check completed for ${current?.label || selected}: ${result.providers?.[0]?.health?.status || 'unknown'}.`);
    } catch (e: any) { setMessage(e.message || 'Provider health check failed'); }
    finally { setBusy(''); }
  };

  const activate = async () => {
    setBusy('activate'); setMessage('');
    try {
      const result = await apiClient.activateIntelligenceProvider(selected); await load(); setActiveProvider(result.active_provider);
      setMessage(`${current?.label || selected} is now the global active AI provider. Routing requires a fresh successful health check.`);
    } catch (e: any) { setMessage(e.message || 'Unable to activate provider'); }
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

  return (
    <CareerOSShell>
      <PageHeader
        eyebrow="Project Control · Global Intelligence"
        title="Global Intelligence Engine"
        description="One provider-neutral AI gateway for every CareerOS intelligence workload. Provider credentials are platform configuration, not user profile data."
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
              <div className="rounded-xl border p-3"><p className="font-semibold">PROVIDER CONTROL</p><div className="mt-2 text-muted-foreground">Registry · Credentials</div></div>
              <div className="rounded-xl border p-3"><p className="font-semibold">RUNTIME CONTROL</p><div className="mt-2 text-muted-foreground">Task Routing · Fallback</div></div>
            </div>
            <div className="mx-auto h-5 w-px border-l" />
            <div className="mx-auto w-fit rounded-xl border px-8 py-2 font-semibold">HEALTH GATE</div>
            <div className="mx-auto h-5 w-px border-l" />
            <div className="grid grid-cols-2 gap-8"><div className="rounded-xl border p-2">Health / Latency</div><div className="rounded-xl border p-2">Quota</div></div>
            <div className="mx-auto h-5 w-px border-l" />
            <div className="mx-auto w-fit rounded-xl border px-8 py-2 font-semibold">AI GATEWAY</div>
            <div className="mx-auto h-5 w-px border-l" />
            <div className="flex justify-center gap-2 text-[10px]">{PROVIDER_CATALOG.map((p) => <span key={p.provider} className="rounded-lg border px-2 py-1">{p.label}</span>)}</div>
          </div>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-4">
        <Card><p className="text-xs text-muted-foreground">Global active provider</p><p className="mt-2 font-semibold">{activeProvider || 'Not selected'}</p></Card>
        <Card><p className="text-xs text-muted-foreground">Gateway</p><p className="mt-2 font-semibold">{gatewayError ? 'Unavailable' : status?.status || 'Checking…'}</p>{gatewayError && <p className="mt-1 text-[11px] text-muted-foreground">{gatewayError}</p>}</Card>
        <Card><p className="text-xs text-muted-foreground">Live requests</p><p className="mt-2 font-semibold">{usage.requests ?? 0}</p></Card>
        <Card><p className="text-xs text-muted-foreground">Fallbacks</p><p className="mt-2 font-semibold">{usage.fallback_requests ?? 0}</p></Card>
      </div>

      <Card className="mt-5" title="Provider registry">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {providers.map((p) => {
            const fresh = Boolean(p.health_fresh);
            return <button key={p.provider} type="button" onClick={() => selectProvider(p.provider)} className={`rounded-2xl border p-4 text-left transition ${selected === p.provider ? 'border-primary bg-primary/5' : 'hover:bg-muted/40'}`}>
              <div className="flex items-center justify-between gap-3"><div><p className="font-semibold">{p.label}</p><p className="mt-1 text-[11px] uppercase tracking-[.12em] text-muted-foreground">{p.category}</p></div><Badge tone={healthTone(p, fresh) as any}>{healthLabel(p, fresh)}</Badge></div>
              <p className="mt-3 text-xs text-muted-foreground">{p.model || 'Model not selected'}</p>
              <p className="mt-1 text-[11px] text-muted-foreground">{p.configured ? 'Configured' : 'Not configured'}{p.active ? ' · Active' : ''}{p.api_key_present ? ` · Key saved ••••${p.api_key_last4}` : ''}</p>
              <div className="mt-3 flex flex-wrap gap-1">{(p.capabilities || []).slice(0, 5).map((x) => <Badge key={x}>{x}</Badge>)}</div>
              <p className="mt-3 text-[11px] text-muted-foreground">Checked: {fmtTime(p.health?.checked_at)}</p>
            </button>;
          })}
        </div>
      </Card>

      {current && <Card className="mt-5" title={`${current.label} configuration`}>
        <div className="rounded-xl border bg-muted/20 p-3 text-xs leading-5 text-muted-foreground">Credentials are encrypted at rest. Save, Test and Activate are separate operations. Health is a separate non-generative gate for activation and runtime routing.</div>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <div><label className="text-xs font-medium">Model</label><input value={form.model} onChange={(e) => setForm((f) => ({ ...f, model: e.target.value }))} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div>
          <div><label className="text-xs font-medium">Priority</label><input type="number" min={1} max={1000} value={form.priority} onChange={(e) => setForm((f) => ({ ...f, priority: Number(e.target.value) || 100 }))} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div>
          {selected !== 'gemini' && <div><label className="text-xs font-medium">Base URL</label><input value={form.base_url} onChange={(e) => setForm((f) => ({ ...f, base_url: e.target.value }))} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div>}
          {selected !== 'ollama' && <div><label className="text-xs font-medium">API key</label><input type="password" value={form.api_key} onChange={(e) => setForm((f) => ({ ...f, api_key: e.target.value }))} placeholder={current.api_key_present ? 'Saved — enter only to replace' : 'Enter API key'} autoComplete="new-password" className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div>}
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button onClick={save} disabled={!!busy}>{busy === 'save' ? 'Saving…' : 'Save Credentials'}</Button>
          <Button onClick={test} disabled={!!busy}>{busy === 'test' ? 'Testing…' : 'Test Connection'}</Button>
          <Button onClick={() => healthCheck(false)} disabled={!!busy}>{busy === 'health' ? 'Checking…' : 'Run Health Check'}</Button>
          <Button onClick={activate} disabled={!!busy || current.active || !currentHealthy}>{busy === 'activate' ? 'Activating…' : current.active ? 'Currently Active' : currentHealthy ? 'Activate Provider' : 'Health Check Required'}</Button>
        </div>
        <p className="mt-3 text-xs text-muted-foreground">Configured keys are reused when switching providers. Activation and AI routing require a fresh successful health check.</p>
      </Card>}

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <Card title="Task-based routing">
          <p className="text-sm text-muted-foreground">Routing order: configured → healthy/fresh → capability match → priority. The active provider is preferred only after the health gate.</p>
          <div className="mt-4 space-y-2">{tasks.map(([key, label]) => <div key={key} className="flex items-center justify-between rounded-lg border px-3 py-2 text-sm"><span>{label}</span><span className="text-xs text-muted-foreground">{(obs?.routing?.tasks?.[key] || []).join(' + ') || 'general'}</span></div>)}</div>
          {observabilityError ? <p className="mt-4 text-xs text-muted-foreground">{observabilityError}</p> : <div className="mt-4 rounded-xl border p-3 text-xs text-muted-foreground">Healthy routing order: {(obs?.routing?.healthy_provider_order || []).join(' → ') || 'No healthy provider yet'}</div>}
        </Card>

        <Card title="Fallback routing">
          <p className="text-sm text-muted-foreground">Fallback is allowed only among configured, compatible, recently healthy providers. Failed generations are recorded before the next eligible candidate is attempted.</p>
          <div className="mt-4 rounded-xl border p-4 space-y-2 text-sm">
            <div className="flex justify-between"><span>Active provider</span><strong>{activeLive?.label || activeProvider || '—'}</strong></div>
            <div className="flex justify-between"><span>Fallback</span><Badge tone={obs?.routing?.fallback_enabled ? 'good' : 'warn'}>{obs?.routing?.fallback_enabled ? 'Enabled' : 'Disabled'}</Badge></div>
            <div className="flex justify-between gap-4"><span>Configured order</span><span className="text-xs text-muted-foreground">{(obs?.routing?.configured_provider_order || []).join(' → ') || '—'}</span></div>
            <div className="flex justify-between gap-4"><span>Healthy order</span><span className="text-xs text-muted-foreground">{(obs?.routing?.healthy_provider_order || []).join(' → ') || '—'}</span></div>
            <div className="flex justify-between"><span>Fallback requests</span><strong>{usage.fallback_requests ?? 0}</strong></div>
          </div>
        </Card>

        <Card title="Usage & cost controls">
          <p className="text-sm text-muted-foreground">Generation telemetry is recorded at the AI boundary. Health is tracked separately. Daily request limits are enforced before generation.</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Requests</p><p className="mt-1 text-lg font-semibold">{usage.requests ?? 0}</p></div>
            <div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Tokens reported</p><p className="mt-1 text-lg font-semibold">{usage.total_tokens ?? 0}</p></div>
            <div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Estimated cost</p><p className="mt-1 text-lg font-semibold">{liveProviders.some((p) => p.telemetry?.estimated_cost !== undefined) ? `$${liveProviders.reduce((n, p) => n + Number(p.telemetry?.estimated_cost || 0), 0).toFixed(4)}` : 'Not reported'}</p></div>
          </div>
          <div className="mt-4 flex flex-wrap items-end gap-3"><div className="min-w-48"><label className="text-xs font-medium">Daily request limit for {current?.label || selected}</label><input type="number" min={1} placeholder="No limit" value={dailyLimit} onChange={(e) => setDailyLimit(e.target.value)} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div><Button onClick={savePolicy} disabled={!!busy}>{busy === 'policy' ? 'Applying…' : 'Apply usage policy'}</Button></div>
        </Card>

        <Card title="Health / latency / quota">
          <p className="text-sm text-muted-foreground">Operational health is measured separately from generation telemetry. Provider quota/rate-limit signals are shown only when supplied by the provider.</p>
          <div className="mt-4 flex flex-wrap gap-2"><Button onClick={() => healthCheck(true)} disabled={!!busy}>{busy === 'health-all' ? 'Checking all…' : 'Run Health Checks'}</Button><span className="self-center text-xs text-muted-foreground">Non-generative health control.</span></div>
          {healthError && <p className="mt-3 text-xs text-muted-foreground">{healthError}</p>}
          <div className="mt-4 overflow-x-auto"><table className="w-full text-left text-xs"><thead><tr className="border-b"><th className="px-2 py-2">Provider</th><th className="px-2 py-2">Health</th><th className="px-2 py-2">Avg</th><th className="px-2 py-2">P95</th><th className="px-2 py-2">Failures</th><th className="px-2 py-2">Quota</th></tr></thead><tbody>{providers.map((p) => { const t = p.health || {}; const fresh = Boolean(p.health_fresh); const quota = t.quota && Object.keys(t.quota).length ? JSON.stringify(t.quota) : 'Not reported'; return <tr key={p.provider} className="border-b last:border-0"><td className="px-2 py-2 font-medium">{p.label}</td><td className="px-2 py-2"><Badge tone={healthTone(p, fresh) as any}>{healthLabel(p, fresh)}</Badge><div className="mt-1 text-[10px] text-muted-foreground">{fmtTime(t.checked_at)}</div></td><td className="px-2 py-2">{fmtMs(t.avg_latency_ms)}</td><td className="px-2 py-2">{fmtMs(t.p95_latency_ms)}</td><td className="px-2 py-2">{t.failed_checks || 0}{t.consecutive_failures ? ` (${t.consecutive_failures} consecutive)` : ''}</td><td className="max-w-56 truncate px-2 py-2" title={quota}>{quota}</td></tr>; })}</tbody></table></div>
          <p className="mt-3 text-[11px] text-muted-foreground">Health freshness window: {Math.round(healthTtl / 60)} minutes.</p>
        </Card>
      </div>

      <Card className="mt-5" title="Architecture boundary">
        <div className="space-y-3 text-sm leading-6 text-muted-foreground">
          <p><strong className="text-foreground">One gateway:</strong> CareerOS modules do not call individual AI vendors directly. Provider health is a control-plane operation through the gateway.</p>
          <p><strong className="text-foreground">Health before routing:</strong> configuration makes a provider eligible for checking; a recent successful health check is required before activation or AI routing. Task capability, priority, policy and fallback are applied after the gate.</p>
          <p><strong className="text-foreground">AI is not the system of record:</strong> AI produces candidate facts, classifications and recommendations. CareerOS services remain authoritative for persistence, validation, provenance, permissions and state transitions.</p>
        </div>
      </Card>
    </CareerOSShell>
  );
}
