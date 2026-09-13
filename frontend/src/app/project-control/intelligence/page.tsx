'use client';

import { useEffect, useMemo, useState } from 'react';
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

type Observability = {
  routing?: any;
  usage?: any;
  providers?: Provider[];
};

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
  ['cv_extraction', 'CV extraction'],
  ['profile_reconciliation', 'Profile reconciliation'],
  ['document_classification', 'Document classification'],
  ['persona_generation', 'Persona generation'],
  ['jd_analysis', 'JD analysis'],
  ['matching', 'Matching'],
  ['research', 'Research'],
  ['interview_intelligence', 'Interview intelligence'],
  ['embedding', 'Embedding'],
  ['bulk_processing', 'Bulk processing'],
];

function healthTone(p: Provider, fresh: boolean) {
  if (p.health?.status === 'healthy' && fresh) return 'good';
  if (p.health?.status === 'unhealthy') return 'warn';
  return p.configured ? 'blue' : 'muted';
}

function healthLabel(p: Provider, fresh: boolean) {
  if (p.health?.status === 'healthy' && fresh) return 'Healthy';
  if (p.health?.status === 'healthy' && !fresh) return 'Stale';
  if (p.health?.status === 'unhealthy') return 'Unhealthy';
  return p.configured ? 'Health check required' : 'Not configured';
}

function fmtTime(value?: string | null) {
  return value ? new Date(value).toLocaleString() : 'Not checked';
}

function fmtMs(value?: number | null) {
  return value == null ? '—' : `${value} ms`;
}

export default function IntelligenceEngine() {
  const [providers, setProviders] = useState<Provider[]>(PROVIDER_CATALOG);
  const [activeProvider, setActiveProvider] = useState('');
  const [selected, setSelected] = useState('ollama');
  const [form, setForm] = useState({ model: '', base_url: '', api_key: '', priority: 100 });
  const [busy, setBusy] = useState('');
  const [message, setMessage] = useState('');
  const [status, setStatus] = useState<any>(null);
  const [obs, setObs] = useState<Observability | null>(null);
  const [dailyLimit, setDailyLimit] = useState('');
  const [healthTtl, setHealthTtl] = useState(900);

  const current = useMemo(() => providers.find((p) => p.provider === selected), [providers, selected]);
  const currentFresh = Boolean(current?.health_fresh);
  const currentHealthy = current?.health?.status === 'healthy' && currentFresh;
  const healthyProviders = providers.filter((p) => p.configured && p.health?.status === 'healthy' && p.health_fresh);
  const liveProviders = obs?.providers?.length ? obs.providers : providers;
  const usage = obs?.usage || {};
  const activeLive = liveProviders.find((p) => p.active);

  const mergeProviders = (remote: Provider[]) => {
    const remoteMap = new Map(remote.map((p) => [p.provider, p]));
    return PROVIDER_CATALOG.map((fallback) => {
      const live = remoteMap.get(fallback.provider);
      return live ? { ...fallback, ...live } : fallback;
    });
  };

  const load = async () => {
    const results = await Promise.allSettled([
      apiClient.intelligenceProviders(),
      apiClient.get('/api/v1/intelligence/status'),
      apiClient.intelligenceObservability(),
      apiClient.intelligenceProviderHealth(),
    ]);

    const [providerResult, statusResult, observabilityResult, healthResult] = results;

    if (providerResult.status === 'fulfilled') {
      const data = providerResult.value;
      const remote = Array.isArray(data.providers) ? data.providers : [];
      const healthData = healthResult.status === 'fulfilled' ? healthResult.value : null;
      const healthMap = new Map((healthData?.providers || []).map((p: any) => [p.provider, p]));
      const merged = mergeProviders(remote).map((p) => {
        const h = healthMap.get(p.provider) as any;
        return {
          ...p,
          health: h?.health || p.health,
          health_fresh: Boolean(h?.health_fresh),
        };
      });
      setProviders(merged);
      setActiveProvider(data.active_provider || '');

      const selectedProvider = merged.find((p) => p.provider === selected) || merged[0];
      if (selectedProvider) {
        setSelected(selectedProvider.provider);
        setForm({
          model: selectedProvider.model || '',
          base_url: selectedProvider.base_url || '',
          api_key: '',
          priority: selectedProvider.priority || 100,
        });
        setDailyLimit(
          selectedProvider.routing_policy?.daily_request_limit
            ? String(selectedProvider.routing_policy.daily_request_limit)
            : '',
        );
      }
    }

    if (statusResult.status === 'fulfilled') setStatus(statusResult.value);
    if (observabilityResult.status === 'fulfilled') setObs(observabilityResult.value);
    if (healthResult.status === 'fulfilled') {
      setHealthTtl(healthResult.value.health_ttl_seconds || 900);
    }

    const failures = results.filter((r) => r.status === 'rejected');
    if (failures.length) {
      const first = failures[0] as PromiseRejectedResult;
      setMessage(first.reason?.message || 'CareerOS API is temporarily unavailable. Provider catalog remains available.');
    }
  };

  useEffect(() => {
    load().catch((e: any) => setMessage(e.message || 'Unable to load Intelligence Engine'));
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => load().catch(() => undefined), 10000);
    return () => window.clearInterval(timer);
  }, [selected]);

  const selectProvider = (name: string) => {
    const p = providers.find((x) => x.provider === name) || PROVIDER_CATALOG.find((x) => x.provider === name);
    if (!p) return;
    setSelected(name);
    setForm({ model: p.model || '', base_url: p.base_url || '', api_key: '', priority: p.priority || 100 });
    setDailyLimit(p.routing_policy?.daily_request_limit ? String(p.routing_policy.daily_request_limit) : '');
    setMessage('');
  };

  const save = async () => {
    setBusy('save');
    setMessage('');
    try {
      await apiClient.saveIntelligenceProvider({
        provider: selected,
        model: form.model || undefined,
        base_url: form.base_url || undefined,
        api_key: form.api_key || undefined,
        priority: form.priority,
      });
      setForm((f) => ({ ...f, api_key: '' }));
      await load();
      setMessage(`${current?.label || selected} credentials/configuration saved. The provider was not activated.`);
    } catch (e: any) {
      setMessage(e.message || 'Unable to save provider');
    } finally {
      setBusy('');
    }
  };

  const test = async () => {
    setBusy('test');
    setMessage('');
    try {
      const result = await apiClient.testIntelligenceProvider({
        provider: selected,
        model: form.model || undefined,
        base_url: form.base_url || undefined,
        api_key: form.api_key || undefined,
      });
      setForm((f) => ({ ...f, api_key: '' }));
      await load();
      setMessage(`Connection test passed: ${result.provider} / ${result.model}`);
    } catch (e: any) {
      setMessage(e.message || 'Provider test failed');
    } finally {
      setBusy('');
    }
  };

  const healthCheck = async (all = false) => {
    setBusy(all ? 'health-all' : 'health');
    setMessage('');
    try {
      const result = await apiClient.runIntelligenceProviderHealthCheck(
        all
          ? {}
          : {
              provider: selected,
              model: form.model || undefined,
              base_url: form.base_url || undefined,
              api_key: form.api_key || undefined,
            },
      );
      setForm((f) => ({ ...f, api_key: '' }));
      await load();
      const ok = (result.providers || []).filter((p: any) => p.health?.status === 'healthy').length;
      setMessage(
        all
          ? `Health check completed: ${ok}/${result.providers?.length || 0} providers healthy.`
          : `Health check completed for ${current?.label || selected}: ${result.providers?.[0]?.health?.status || 'unknown'}.`,
      );
    } catch (e: any) {
      setMessage(e.message || 'Provider health check failed');
    } finally {
      setBusy('');
    }
  };

  const activate = async () => {
    setBusy('activate');
    setMessage('');
    try {
      const result = await apiClient.activateIntelligenceProvider(selected);
      await load();
      setActiveProvider(result.active_provider);
      setMessage(`${current?.label || selected} is now the global active AI provider. Routing requires a fresh successful health check.`);
    } catch (e: any) {
      setMessage(e.message || 'Unable to activate provider');
    } finally {
      setBusy('');
    }
  };

  const savePolicy = async () => {
    setBusy('policy');
    try {
      await apiClient.updateIntelligenceRoutingPolicy({
        provider: selected,
        fallback_enabled: true,
        daily_request_limit: dailyLimit ? Number(dailyLimit) : null,
      });
      await load();
      setMessage(`Runtime policy updated for ${current?.label || selected}.`);
    } catch (e: any) {
      setMessage(e.message || 'Unable to update runtime policy');
    } finally {
      setBusy('');
    }
  };

  return (
    <CareerOSShell>
      <PageHeader
        eyebrow="Project Control · Global Intelligence"
        title="Global Intelligence Engine"
        description="One provider-neutral AI gateway for every CareerOS intelligence workload. Provider credentials are platform configuration, not user profile data."
        action={
          <Badge tone={status?.status === 'ready' ? 'good' : 'warn'}>
            {status?.status === 'ready' ? 'Gateway ready' : status?.status || 'Checking'}
          </Badge>
        }
      />

      {message && (
        <div className="mb-5 rounded-xl border bg-card px-4 py-3 text-sm">
          {message}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <p className="text-xs text-muted-foreground">Global active provider</p>
          <p className="mt-2 font-semibold">{activeProvider || 'Not selected'}</p>
        </Card>
        <Card>
          <p className="text-xs text-muted-foreground">Gateway</p>
          <p className="mt-2 font-semibold">{status?.status || 'Checking…'}</p>
        </Card>
        <Card>
          <p className="text-xs text-muted-foreground">Live requests</p>
          <p className="mt-2 font-semibold">{usage.requests ?? 0}</p>
        </Card>
        <Card>
          <p className="text-xs text-muted-foreground">Fallbacks</p>
          <p className="mt-2 font-semibold">{usage.fallback_requests ?? 0}</p>
        </Card>
      </div>

      <Card className="mt-5" title="Provider registry">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {providers.map((p) => {
            const fresh = Boolean(p.health_fresh);
            return (
              <button
                key={p.provider}
                type="button"
                onClick={() => selectProvider(p.provider)}
                className={`rounded-2xl border p-4 text-left transition ${
                  selected === p.provider ? 'border-primary bg-primary/5' : 'hover:bg-muted/40'
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="font-semibold">{p.label}</p>
                    <p className="mt-1 text-[11px] uppercase tracking-[.12em] text-muted-foreground">{p.category}</p>
                  </div>
                  <Badge tone={healthTone(p, fresh) as any}>
                    {healthLabel(p, fresh)}
                  </Badge>
                </div>
                <p className="mt-3 text-xs text-muted-foreground">{p.model || 'Model not selected'}</p>
                {p.api_key_present && (
                  <p className="mt-1 text-[11px] text-muted-foreground">Key saved · ••••{p.api_key_last4}</p>
                )}
                <div className="mt-3 flex flex-wrap gap-1">
                  {(p.capabilities || []).slice(0, 5).map((x) => <Badge key={x}>{x}</Badge>)}
                </div>
                <p className="mt-3 text-[11px] text-muted-foreground">
                  {p.active ? 'Active · ' : ''}Checked: {fmtTime(p.health?.checked_at)}
                </p>
              </button>
            );
          })}
        </div>
      </Card>

      {current && (
        <Card className="mt-5" title={`${current.label} configuration`}>
          <div className="rounded-xl border bg-muted/20 p-3 text-xs leading-5 text-muted-foreground">
            Credentials are encrypted at rest. The API never returns the secret. Save, Test and Activate remain separate operations. Activation and AI routing additionally require a recent successful health check.
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <div>
              <label className="text-xs font-medium">Model</label>
              <input
                value={form.model}
                onChange={(e) => setForm((f) => ({ ...f, model: e.target.value }))}
                className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="text-xs font-medium">Priority</label>
              <input
                type="number"
                min={1}
                max={1000}
                value={form.priority}
                onChange={(e) => setForm((f) => ({ ...f, priority: Number(e.target.value) || 100 }))}
                className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm"
              />
            </div>

            {selected !== 'gemini' && (
              <div>
                <label className="text-xs font-medium">Base URL</label>
                <input
                  value={form.base_url}
                  onChange={(e) => setForm((f) => ({ ...f, base_url: e.target.value }))}
                  className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm"
                />
              </div>
            )}

            {selected !== 'ollama' && (
              <div>
                <label className="text-xs font-medium">API key</label>
                <input
                  type="password"
                  value={form.api_key}
                  onChange={(e) => setForm((f) => ({ ...f, api_key: e.target.value }))}
                  placeholder={current.api_key_present ? 'Saved — enter only to replace' : 'Enter API key'}
                  autoComplete="new-password"
                  className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm"
                />
              </div>
            )}
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            <Button onClick={save} disabled={!!busy}>
              {busy === 'save' ? 'Saving…' : 'Save Credentials'}
            </Button>
            <Button onClick={test} disabled={!!busy}>
              {busy === 'test' ? 'Testing…' : 'Test Connection'}
            </Button>
            <Button onClick={() => healthCheck(false)} disabled={!!busy}>
              {busy === 'health' ? 'Checking…' : 'Run Health Check'}
            </Button>
            <Button onClick={activate} disabled={!!busy || current.active || !currentHealthy}>
              {busy === 'activate'
                ? 'Activating…'
                : current.active
                  ? 'Currently Active'
                  : currentHealthy
                    ? 'Activate Provider'
                    : 'Health Check Required'}
            </Button>
          </div>

          <p className="mt-3 text-xs text-muted-foreground">
            Switching providers later only requires selecting a configured provider and activating it after a fresh successful health check. The saved key is reused.
          </p>
        </Card>
      )}

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <Card title="Task-based routing">
          <p className="text-sm text-muted-foreground">
            Routing order: configured → healthy/fresh → capability match → priority. The active provider is preferred only when it passes the health gate.
          </p>
          <div className="mt-4 space-y-2">
            {tasks.map(([key, label]) => (
              <div key={key} className="flex items-center justify-between rounded-lg border px-3 py-2 text-sm">
                <span>{label}</span>
                <span className="text-xs text-muted-foreground">
                  {(obs?.routing?.tasks?.[key] || []).join(' + ') || 'general'}
                </span>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-xl border p-3 text-xs text-muted-foreground">
            Healthy routing order: {(obs?.routing?.healthy_provider_order || []).join(' → ') || 'No healthy provider yet'}
          </div>
        </Card>

        <Card title="Fallback routing">
          <p className="text-sm text-muted-foreground">
            Fallback is allowed only among configured, compatible, recently healthy providers. A failed generation is recorded and the next healthy candidate may be attempted according to policy.
          </p>
          <div className="mt-4 rounded-xl border p-4">
            <div className="flex justify-between text-sm">
              <span>Active provider</span>
              <strong>{activeLive?.label || activeProvider || '—'}</strong>
            </div>
            <div className="mt-2 flex justify-between text-sm">
              <span>Fallback</span>
              <Badge tone={obs?.routing?.fallback_enabled ? 'good' : 'warn'}>
                {obs?.routing?.fallback_enabled ? 'Enabled' : 'Disabled'}
              </Badge>
            </div>
            <div className="mt-2 flex justify-between text-sm">
              <span>Configured order</span>
              <span className="text-xs text-muted-foreground">
                {(obs?.routing?.configured_provider_order || []).join(' → ') || '—'}
              </span>
            </div>
            <div className="mt-2 flex justify-between text-sm">
              <span>Healthy order</span>
              <span className="text-xs text-muted-foreground">
                {(obs?.routing?.healthy_provider_order || []).join(' → ') || '—'}
              </span>
            </div>
            <div className="mt-2 flex justify-between text-sm">
              <span>Fallback requests</span>
              <strong>{usage.fallback_requests ?? 0}</strong>
            </div>
          </div>
        </Card>

        <Card title="Usage & cost controls">
          <p className="text-sm text-muted-foreground">
            Usage is recorded at the generation boundary. Health checks are tracked separately so operational checks do not inflate AI request usage. Daily request limits are enforced before generation.
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border p-3">
              <p className="text-xs text-muted-foreground">Requests</p>
              <p className="mt-1 text-lg font-semibold">{usage.requests ?? 0}</p>
            </div>
            <div className="rounded-xl border p-3">
              <p className="text-xs text-muted-foreground">Tokens reported</p>
              <p className="mt-1 text-lg font-semibold">{usage.total_tokens ?? 0}</p>
            </div>
            <div className="rounded-xl border p-3">
              <p className="text-xs text-muted-foreground">Estimated cost</p>
              <p className="mt-1 text-lg font-semibold">
                {liveProviders.some((p) => p.telemetry?.estimated_cost !== undefined)
                  ? `$${liveProviders.reduce((n, p) => n + Number(p.telemetry?.estimated_cost || 0), 0).toFixed(4)}`
                  : 'Not reported'}
              </p>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap items-end gap-3">
            <div className="min-w-48">
              <label className="text-xs font-medium">Daily request limit for {current?.label || selected}</label>
              <input
                type="number"
                min={1}
                placeholder="No limit"
                value={dailyLimit}
                onChange={(e) => setDailyLimit(e.target.value)}
                className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm"
              />
            </div>
            <Button onClick={savePolicy} disabled={!!busy}>
              {busy === 'policy' ? 'Applying…' : 'Apply usage policy'}
            </Button>
          </div>
        </Card>

        <Card title="Health / latency / quota">
          <p className="text-sm text-muted-foreground">
            Operational health is measured separately from generation telemetry. Provider-reported quota/rate-limit signals are shown only when returned by the provider; CareerOS limits remain separate.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button onClick={() => healthCheck(true)} disabled={!!busy}>
              {busy === 'health-all' ? 'Checking all…' : 'Run Health Checks'}
            </Button>
            <span className="self-center text-xs text-muted-foreground">
              No generation request is made by this health control.
            </span>
          </div>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b">
                  <th className="px-2 py-2">Provider</th>
                  <th className="px-2 py-2">Health</th>
                  <th className="px-2 py-2">Avg</th>
                  <th className="px-2 py-2">P95</th>
                  <th className="px-2 py-2">Failures</th>
                  <th className="px-2 py-2">Quota</th>
                </tr>
              </thead>
              <tbody>
                {providers.map((p) => {
                  const t = p.health || {};
                  const fresh = Boolean(p.health_fresh);
                  const quota = t.quota && Object.keys(t.quota).length ? JSON.stringify(t.quota) : 'Not reported';
                  return (
                    <tr key={p.provider} className="border-b last:border-0">
                      <td className="px-2 py-2 font-medium">{p.label}</td>
                      <td className="px-2 py-2">
                        <Badge tone={healthTone(p, fresh) as any}>{healthLabel(p, fresh)}</Badge>
                        <div className="mt-1 text-[10px] text-muted-foreground">{fmtTime(t.checked_at)}</div>
                      </td>
                      <td className="px-2 py-2">{fmtMs(t.avg_latency_ms)}</td>
                      <td className="px-2 py-2">{fmtMs(t.p95_latency_ms)}</td>
                      <td className="px-2 py-2">
                        {t.failed_checks || 0}
                        {t.consecutive_failures ? ` (${t.consecutive_failures} consecutive)` : ''}
                      </td>
                      <td className="max-w-56 truncate px-2 py-2" title={quota}>{quota}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-[11px] text-muted-foreground">Health freshness window: {Math.round(healthTtl / 60)} minutes.</p>
        </Card>
      </div>

      <Card className="mt-5" title="Architecture boundary">
        <div className="space-y-3 text-sm leading-6 text-muted-foreground">
          <p><strong className="text-foreground">One gateway:</strong> CareerOS modules do not call individual AI vendors directly. Provider health is a control-plane operation through the gateway.</p>
          <p><strong className="text-foreground">Health before routing:</strong> configuration is only eligibility metadata. A provider must pass a recent non-generative health check before activation or AI routing. Routing then applies task capability, priority, policy and fallback.</p>
          <p><strong className="text-foreground">AI is not the system of record:</strong> AI produces candidate facts, classifications and recommendations. CareerOS application services remain authoritative for persistence, validation, provenance, permissions and state transitions.</p>
        </div>
      </Card>
    </CareerOSShell>
  );
}
