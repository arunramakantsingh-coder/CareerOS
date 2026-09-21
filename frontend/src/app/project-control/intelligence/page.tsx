'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { CareerOSShell, PageHeader, Card, Badge, Button } from '@/components/CareerOSShell';
import LiveExecutionPanel from '@/components/intelligence/LiveExecutionPanel';
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
  configuration_valid?: boolean;
  configuration_error?: string | null;
  routing_policy?: any;
  telemetry?: any;
  health?: ProviderHealth;
  health_fresh?: boolean;
};

type HealthPolicy = { enabled: boolean; interval_seconds: number; grace_seconds: number; health_ttl_seconds: number };
type ProviderForm = { model: string; base_url: string; api_key: string; priority: number };
type ModelOption = { name: string; source?: string; parameter_size?: string; family?: string };

const PROVIDER_CATALOG: Provider[] = [
  { provider: 'ollama', label: 'Ollama', category: 'local', model: 'gemma3:4b', base_url: 'http://host.docker.internal:11434', configured: false, active: false, priority: 100, capabilities: ['local', 'private', 'structured_output', 'reasoning'] },
  { provider: 'openrouter', label: 'OpenRouter', category: 'cloud', model: 'google/gemma-4-26b-a4b-it:free', base_url: 'https://openrouter.ai/api/v1', configured: false, active: false, priority: 100, capabilities: ['routing', 'model_choice', 'structured_output', 'reasoning'] },
  { provider: 'openai', label: 'OpenAI', category: 'cloud', model: 'gpt-5.6-luna', base_url: 'https://api.openai.com/v1', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'structured_output', 'vision'] },
  { provider: 'gemini', label: 'Google Gemini', category: 'cloud', model: 'gemini-3.5-flash-lite', base_url: '', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'structured_output', 'long_context'] },
  { provider: 'anthropic', label: 'Anthropic Claude', category: 'cloud', model: 'claude-sonnet-5', base_url: 'https://api.anthropic.com', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'long_context', 'structured_output'] },
  { provider: 'mistral', label: 'Mistral AI', category: 'cloud', model: 'mistral-large-latest', base_url: 'https://api.mistral.ai/v1', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'structured_output', 'document_intelligence'] },
  { provider: 'xai', label: 'xAI', category: 'cloud', model: 'grok-4.6', base_url: 'https://api.x.ai/v1', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'vision', 'web_search'] },
  { provider: 'groq', label: 'Groq', category: 'cloud', model: 'llama-4-scout-17b-16e-instruct', base_url: 'https://api.groq.com/openai/v1', configured: false, active: false, priority: 100, capabilities: ['fast', 'structured_output'] },
  { provider: 'deepseek', label: 'DeepSeek', category: 'cloud', model: 'deepseek-v4-pro', base_url: 'https://api.deepseek.com', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'coding', 'structured_output', 'long_context'] },

  { provider: 'ainterceptor', label: 'AInterceptor', category: 'self-hosted', model: 'deepseek', base_url: 'https://ainterceptor.taila2310c.ts.net/v1', configured: false, active: false, priority: 100, capabilities: ['reasoning', 'coding', 'structured_output'] },
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

function healthLabel(p: Provider, fresh: boolean) { if (!p.configured) return 'NOT CHECKED'; if (p.health?.status === 'healthy' && fresh) return 'HEALTHY'; if (p.health?.status === 'healthy') return 'STALE'; if (p.health?.status === 'unhealthy') return 'UNHEALTHY'; return 'NOT CHECKED'; }
function healthTone(p: Provider, fresh: boolean) { const label = healthLabel(p, fresh); if (label === 'HEALTHY') return 'good'; if (label === 'UNHEALTHY') return 'warn'; if (label === 'STALE') return 'blue'; return 'muted'; }
function lifecycleLabel(p: Provider) { if (!p.configured) return 'NOT CONFIGURED'; return p.active ? 'ACTIVE' : 'DEACTIVATED'; }
function lifecycleTone(p: Provider) { return !p.configured ? 'muted' : p.active ? 'good' : 'blue'; }
function fmtTime(v?: string | null) { return v ? new Date(v).toLocaleString() : 'Not checked'; }
function fmtMs(v?: number | null) { return v == null ? '—' : `${Number(v).toFixed(1)} ms`; }
function fmtInterval(seconds: number) { if (seconds % 3600 === 0) return `${seconds / 3600} hour${seconds === 3600 ? '' : 's'}`; if (seconds % 60 === 0) return `${seconds / 60} minutes`; return `${seconds} seconds`; }

export default function IntelligenceEngine() {
  const [providers, setProviders] = useState<Provider[]>(PROVIDER_CATALOG);
  const [selected, setSelected] = useState('ollama');
  const [form, setForm] = useState<ProviderForm>({ model: '', base_url: '', api_key: '', priority: 100 });
  const [modelOptions, setModelOptions] = useState<ModelOption[]>([]);
  const [modelLoading, setModelLoading] = useState(false);
  const [busy, setBusy] = useState(''); const [message, setMessage] = useState(''); const [registryError, setRegistryError] = useState(''); const [gatewayError, setGatewayError] = useState(''); const [healthError, setHealthError] = useState('');
  const [status, setStatus] = useState<any>(null);
  const [healthPolicy, setHealthPolicy] = useState<HealthPolicy>({ enabled: true, interval_seconds: 900, grace_seconds: 60, health_ttl_seconds: 960 });
  const [routing, setRouting] = useState<any>(null); const [taskType, setTaskType] = useState('profile_reconciliation'); const [latestTrace, setLatestTrace] = useState<any>(null);
  const [liveTraceId, setLiveTraceId] = useState<string | null>(null); const [liveTrace, setLiveTrace] = useState<any>(null); const [showLivePanel, setShowLivePanel] = useState(false); const [liveMode, setLiveMode] = useState<'health' | 'connection' | null>(null); const [liveStartedAt, setLiveStartedAt] = useState(0); const [liveClock, setLiveClock] = useState(Date.now());
  const loadingRef = useRef(false); const selectedRef = useRef('ollama'); const hydratedProviderRef = useRef<string | null>(null);

  const current = useMemo(() => providers.find((p) => p.provider === selected) || PROVIDER_CATALOG.find((p) => p.provider === selected), [providers, selected]);
  const activeProviders = providers.filter((p) => p.active && p.configured); const configuredCount = providers.filter((p) => p.configured).length; const healthyCount = providers.filter((p) => p.configured && p.health?.status === 'healthy' && p.health_fresh).length; const lastHealthCheck = providers.map((p) => p.health?.checked_at).filter(Boolean).sort().at(-1);

  const mergeProviders = (remote: Provider[], healthData?: any) => {
    const remoteMap = new Map(remote.map((p) => [p.provider, p])); const healthMap = new Map((healthData?.providers || []).map((p: any) => [p.provider, p]));
    return PROVIDER_CATALOG.map((fallback) => { const live = remoteMap.get(fallback.provider); const h: any = healthMap.get(fallback.provider); return { ...fallback, ...(live || {}), health: h?.health || live?.health || fallback.health, health_fresh: h ? Boolean(h.health_fresh) : Boolean(live?.health_fresh) }; });
  };

  const formForProvider = (list: Provider[], name: string): ProviderForm | null => {
    const p = list.find((x) => x.provider === name) || PROVIDER_CATALOG.find((x) => x.provider === name); if (!p) return null; const catalog = PROVIDER_CATALOG.find((x) => x.provider === name) || p; const invalid = p.configuration_valid === false;
    return { model: invalid ? catalog.model || '' : p.model || '', base_url: invalid ? catalog.base_url || '' : p.base_url || '', api_key: '', priority: p.priority || 100 };
  };
  const hydrateSelectedForm = (list: Provider[], name = selectedRef.current) => { const next = formForProvider(list, name); if (!next) return; setForm(next); hydratedProviderRef.current = name; };

  const loadModels = async (name = selectedRef.current) => {
    setModelLoading(true);
    try {
      const result = await apiClient.intelligenceProviderModels(name);
      setModelOptions(Array.isArray(result?.models) ? result.models : []);
    } catch (e: any) {
      setModelOptions([]);
      setMessage(e?.message || `Unable to detect ${name} models.`);
    } finally { setModelLoading(false); }
  };

  const load = async () => {
    if (loadingRef.current) return; loadingRef.current = true;
    const results = await Promise.allSettled([apiClient.intelligenceProviders(), apiClient.get('/api/v1/intelligence/status'), apiClient.intelligenceProviderHealth(), apiClient.intelligenceProviderHealthPolicy(), apiClient.intelligenceRoutingPreview(taskType), apiClient.intelligenceRuntimeTraces(10)]);
    const [registryResult, statusResult, healthResult, policyResult, routingResult, tracesResult] = results;
    if (registryResult.status === 'fulfilled') {
      const data = registryResult.value; const base = mergeProviders(Array.isArray(data.providers) ? data.providers : []); setProviders(base);
      const selectedName = selectedRef.current; if (hydratedProviderRef.current !== selectedName) hydrateSelectedForm(base, selectedName);
    } else setRegistryError(registryResult.reason?.message || 'Unable to load provider registry.');
    if (statusResult.status === 'fulfilled') { setStatus(statusResult.value); setGatewayError(''); } else { setStatus(null); setGatewayError('Gateway status unavailable.'); }
    if (healthResult.status === 'fulfilled') { const data = healthResult.value; setHealthError(''); if (data.health_policy) setHealthPolicy((p) => ({ ...p, ...data.health_policy, health_ttl_seconds: data.health_ttl_seconds || p.health_ttl_seconds })); setProviders((previous) => mergeProviders(previous, data)); } else setHealthError('Health data unavailable.');
    if (policyResult.status === 'fulfilled') setHealthPolicy(policyResult.value); if (routingResult.status === 'fulfilled') setRouting(routingResult.value);
    if (tracesResult.status === 'fulfilled') { const trace = (tracesResult.value.traces || []).find((x: any) => x.task_type === taskType); setLatestTrace(trace || null); }
    loadingRef.current = false;
  };

  useEffect(() => { void load(); }, [taskType]); useEffect(() => { const timer = window.setInterval(() => void load(), 15000); return () => window.clearInterval(timer); }, [taskType]);
  useEffect(() => { void loadModels(selected); }, [selected]);

  const selectProvider = (name: string) => { const p = providers.find((x) => x.provider === name) || PROVIDER_CATALOG.find((x) => x.provider === name); if (!p) return; selectedRef.current = name; setSelected(name); hydrateSelectedForm(providers, name); setMessage(''); };

  const save = async () => { setBusy('save'); setMessage(''); try { const provider = selectedRef.current; await apiClient.saveIntelligenceProvider({ provider, model: form.model || undefined, base_url: provider === 'gemini' ? undefined : form.base_url || undefined, api_key: form.api_key || undefined, priority: form.priority }); hydrateSelectedForm(providers, provider); await load(); setMessage(`${current?.label || provider} configuration saved. Activation remains a separate operator action.`); } catch (e: any) { setMessage(e.message || 'Unable to save provider'); } finally { setBusy(''); } };

  const test = async () => { setBusy('test'); setMessage(''); try { const provider = selectedRef.current; const result = await apiClient.testIntelligenceProvider({ provider, model: form.model || undefined, base_url: provider === 'gemini' ? undefined : form.base_url || undefined, api_key: form.api_key || undefined }); setForm((f) => ({ ...f, api_key: '' })); await load(); setMessage(`Connection test ${result.provider} / ${result.model} completed successfully.`); } catch (e: any) { setMessage(e.message || 'Provider test failed'); } finally { setBusy(''); } };

  const healthCheck = async (all = false) => { setBusy(all ? 'health-all' : 'health'); setMessage(''); try { const provider = selectedRef.current; const result = await apiClient.runIntelligenceProviderHealthCheck(all ? {} : { provider, model: form.model || undefined, base_url: provider === 'gemini' ? undefined : form.base_url || undefined, api_key: form.api_key || undefined }); setForm((f) => ({ ...f, api_key: '' })); await load(); const ok = (result.providers || []).filter((p: any) => p.health?.status === 'healthy').length; setMessage(all ? `Health check completed: ${ok}/${result.providers?.length || 0} configured providers healthy.` : `Health check completed for ${current?.label || provider}: ${result.providers?.[0]?.health?.status || 'unknown'}.`); } catch (e: any) { setMessage(e.message || 'Provider health check failed'); } finally { setBusy(''); } };
  const activate = async () => { setBusy('activate'); setMessage(''); try { const provider = selectedRef.current; await apiClient.activateIntelligenceProvider(provider); await load(); setMessage(`${current?.label || provider} activated as the operator-preferred provider. Other active eligible providers remain available for dynamic routing/fallback.`); } catch (e: any) { setMessage(e.message || 'Unable to activate provider'); } finally { setBusy(''); } };
  const deactivate = async () => { setBusy('deactivate'); setMessage(''); try { const provider = selectedRef.current; await apiClient.deactivateIntelligenceProvider(provider); await load(); setMessage(`${current?.label || provider} manually deactivated. It is excluded from runtime routing and fallback regardless of health or priority.`); } catch (e: any) { setMessage(e.message || 'Unable to deactivate provider'); } finally { setBusy(''); } };
  const saveHealthPolicy = async () => { setBusy('health-policy'); setMessage(''); try { const result = await apiClient.updateIntelligenceProviderHealthPolicy(healthPolicy); setHealthPolicy(result); await load(); setMessage(`Automatic health checks ${result.enabled ? 'enabled' : 'disabled'} at ${fmtInterval(result.interval_seconds)} intervals.`); } catch (e: any) { setMessage(e.message || 'Unable to update automatic health policy'); } finally { setBusy(''); } };

  const nextHealthCheck = lastHealthCheck ? new Date(new Date(lastHealthCheck).getTime() + healthPolicy.interval_seconds * 1000) : null; const traceAttempts = latestTrace?.attempts || [];

  return (
    <CareerOSShell>
      <PageHeader eyebrow="Project Control · Global Intelligence" title="Global Intelligence Engine" description="Central control plane for provider configuration, lifecycle, health, task routing, fallback and runtime eligibility across CareerOS." action={<Badge tone={status?.status === 'ready' ? 'good' : 'warn'}>{status?.status === 'ready' ? 'Gateway ready' : status?.status || 'Checking'}</Badge>} />
      {registryError && <div className="mb-3 rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm">{registryError}</div>}{message && <div className="mb-5 rounded-xl border bg-card px-4 py-3 text-sm">{message}</div>}
      <Card className="mb-5" title="Global Intelligence control plane"><div className="overflow-x-auto rounded-xl border bg-muted/10 p-4"><div className="min-w-[760px] text-center font-mono text-xs"><div className="mx-auto w-fit rounded-xl border px-6 py-2 font-semibold">GLOBAL INTELLIGENCE ENGINE</div><div className="mx-auto h-5 w-px border-l" /><div className="grid grid-cols-2 gap-8"><div className="rounded-xl border p-3"><p className="font-semibold">PROVIDER CONTROL</p><div className="mt-2 text-muted-foreground">Registry · Credentials · Activate / Deactivate</div></div><div className="rounded-xl border p-3"><p className="font-semibold">RUNTIME CONTROL</p><div className="mt-2 text-muted-foreground">Task Routing · Ranking · Fallback</div></div></div><div className="mx-auto h-5 w-px border-l" /><div className="mx-auto w-fit rounded-xl border px-8 py-2 font-semibold">HEALTH GATE</div><div className="mx-auto h-5 w-px border-l" /><div className="grid grid-cols-2 gap-8"><div className="rounded-xl border p-2">Health / Latency</div><div className="rounded-xl border p-2">Quota / Rate limits</div></div><div className="mx-auto h-5 w-px border-l" /><div className="mx-auto w-fit rounded-xl border px-8 py-2 font-semibold">AI GATEWAY</div><div className="mx-auto h-5 w-px border-l" /><div className="flex justify-center gap-2 text-[10px]">{PROVIDER_CATALOG.map((p) => <span key={p.provider} className="rounded-lg border px-2 py-1">{p.label}</span>)}</div></div></div></Card>
      <div className="grid gap-4 md:grid-cols-4"><Card><p className="text-xs text-muted-foreground">Active providers</p><p className="mt-2 font-semibold">{activeProviders.length}</p></Card><Card><p className="text-xs text-muted-foreground">Configured</p><p className="mt-2 font-semibold">{configuredCount}</p></Card><Card><p className="text-xs text-muted-foreground">Healthy & fresh</p><p className="mt-2 font-semibold">{healthyCount}</p></Card><Card><p className="text-xs text-muted-foreground">Gateway</p><p className="mt-2 font-semibold">{gatewayError ? 'Unavailable' : status?.status || 'Checking…'}</p></Card></div>
      <Card className="mt-5" title="Automatic provider health checks"><div className="rounded-xl border bg-muted/20 p-3 text-xs leading-5 text-muted-foreground">The backend scheduler runs independently of the browser. STALE means the last successful health result exists but has exceeded the configured freshness TTL. STALE is not the same as UNHEALTHY. Automatic checks are non-generative control-plane checks.</div><div className="mt-4 grid gap-4 md:grid-cols-5"><label className="flex items-center gap-3 rounded-xl border p-3"><input type="checkbox" checked={healthPolicy.enabled} onChange={(e) => setHealthPolicy((p) => ({ ...p, enabled: e.target.checked }))} /><span><span className="block text-sm font-semibold">Automatic checks</span><span className="text-xs text-muted-foreground">Backend scheduler</span></span></label><label><span className="text-xs font-medium">Check interval</span><select value={healthPolicy.interval_seconds} onChange={(e) => setHealthPolicy((p) => ({ ...p, interval_seconds: Number(e.target.value) }))} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm">{HEALTH_INTERVALS.map((s) => <option key={s} value={s}>{fmtInterval(s)}</option>)}</select></label><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Last check</p><p className="mt-1 text-sm font-semibold">{fmtTime(lastHealthCheck)}</p></div><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Next check</p><p className="mt-1 text-sm font-semibold">{nextHealthCheck ? nextHealthCheck.toLocaleString() : 'Scheduled on startup'}</p></div><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Freshness TTL</p><p className="mt-1 text-sm font-semibold">{fmtInterval(healthPolicy.health_ttl_seconds)}</p></div></div><div className="mt-4 flex flex-wrap gap-2"><Button onClick={saveHealthPolicy} disabled={!!busy}>{busy === 'health-policy' ? 'Saving…' : 'Save Health Policy'}</Button><Button onClick={() => healthCheck(true)} disabled={!!busy}>{busy === 'health-all' ? 'Checking all…' : 'Run Health Check Now'}</Button><span className="self-center text-xs text-muted-foreground">Interval {fmtInterval(healthPolicy.interval_seconds)} · grace {fmtInterval(healthPolicy.grace_seconds)}</span></div></Card>
      <Card className="mt-5" title="Provider registry"><p className="mb-4 text-sm text-muted-foreground">Lifecycle and health are separate dimensions. Cards intentionally show only provider identity plus lifecycle and health; routing metrics live in the sections below.</p><div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">{providers.map((p) => <button key={p.provider} type="button" onClick={() => selectProvider(p.provider)} className={`rounded-2xl border p-4 text-left transition ${selected === p.provider ? 'border-primary bg-primary/5 shadow-sm' : 'hover:bg-muted/40'}`}><div className="flex items-start justify-between gap-3"><div><p className="font-semibold">{p.label}</p><p className="mt-1 text-[11px] uppercase tracking-[.12em] text-muted-foreground">{p.category}</p></div><div className="flex flex-wrap justify-end gap-1"><Badge tone={lifecycleTone(p) as any}>{lifecycleLabel(p)}</Badge><Badge tone={healthTone(p, Boolean(p.health_fresh)) as any}>{healthLabel(p, Boolean(p.health_fresh))}</Badge></div></div></button>)}</div></Card>
      {current && <Card className="mt-5" title={`${current.label} provider configuration`}><div className="rounded-xl border bg-muted/20 p-3 text-xs leading-5 text-muted-foreground">Manual deactivation prevents runtime selection and fallback. Saving credentials does not activate a provider. A provider must be configured, valid, active, fresh-healthy, task-compatible and policy-eligible before runtime can select it.</div>{current.configuration_valid === false && <div className="mt-3 rounded-xl border border-destructive/30 bg-destructive/5 px-3 py-2 text-xs"><strong>Stored configuration is invalid for this provider.</strong> {current.configuration_error || 'It will not be routed. The form below is showing safe provider defaults; Save Credentials to replace the invalid model/endpoint.'}</div>}<div className="mt-4 grid gap-3 md:grid-cols-2"><div><label className="text-xs font-medium">Model</label><select value={form.model} onChange={(e) => setForm((f) => ({ ...f, model: e.target.value }))} disabled={modelLoading || !modelOptions.length} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm">{!modelOptions.length && <option value={form.model}>{modelLoading ? 'Detecting models…' : form.model || 'No model detected'}</option>}{form.model && !modelOptions.some((item) => item.name === form.model) && <option value={form.model}>{form.model} · current configuration</option>}{modelOptions.map((item) => <option key={item.name} value={item.name}>{item.name}{item.parameter_size ? ` · ${item.parameter_size}` : ''}{item.source === 'ollama_local' ? ' · local' : ''}</option>)}</select><div className="mt-1 flex items-center justify-between gap-2"><p className="text-[11px] text-muted-foreground">{selected === 'ollama' ? 'Detected from the locally running Ollama model catalog.' : 'Configured/catalog model options.'}</p><button type="button" onClick={() => void loadModels()} disabled={modelLoading} className="text-[11px] font-medium underline">{modelLoading ? 'Detecting…' : 'Refresh models'}</button></div></div><div><label className="text-xs font-medium">Manual priority</label><input type="number" min={1} max={1000} value={form.priority} onChange={(e) => setForm((f) => ({ ...f, priority: Number(e.target.value) || 100 }))} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /><p className="mt-1 text-[11px] text-muted-foreground">Operator preference / final tie-breaker only. It cannot override health, task compatibility, lifecycle or policy gates.</p></div><div><label className="text-xs font-medium">Base URL</label><input value={selected === 'gemini' ? 'Native Google Gemini API endpoint' : form.base_url} disabled={selected === 'gemini'} onChange={(e) => setForm((f) => ({ ...f, base_url: e.target.value }))} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm disabled:opacity-70" /><p className="mt-1 text-[11px] text-muted-foreground">{selected === 'gemini' ? 'Gemini owns its native endpoint; an Ollama/OpenAI-compatible endpoint is never accepted.' : 'Provider-specific endpoint; cross-provider endpoints are rejected.'}</p></div><div><label className="text-xs font-medium">API key</label><input type="password" value={form.api_key} onChange={(e) => setForm((f) => ({ ...f, api_key: e.target.value }))} placeholder={current.api_key_present ? `Saved — enter only to replace ••••${current.api_key_last4 || ''}` : selected === 'ollama' ? 'Not required for local Ollama' : 'Enter API key'} autoComplete="new-password" className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm" /></div></div><div className="mt-4 flex flex-wrap gap-2"><Button onClick={save} disabled={!!busy}>{busy === 'save' ? 'Saving…' : 'Save Credentials'}</Button><Button onClick={test} disabled={!!busy}>{busy === 'test' ? 'Testing…' : 'Test Connection'}</Button><Button onClick={() => healthCheck(false)} disabled={!!busy}>{busy === 'health' ? 'Checking…' : 'Run Health Check'}</Button>{current.active ? <Button onClick={deactivate} disabled={!!busy}> {busy === 'deactivate' ? 'Deactivating…' : 'Deactivate Provider'} </Button> : <Button onClick={activate} disabled={!!busy || !current.configured || !currentHealthy(current)}>{busy === 'activate' ? 'Activating…' : current.configured ? currentHealthy(current) ? 'Activate Provider' : 'Health Check Required' : 'Configure Provider First'}</Button>}</div></Card>}
      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <Card title="Task-based routing"><div className="flex flex-wrap items-end justify-between gap-3"><div><p className="text-sm text-muted-foreground">Runtime preview uses the same hard gates and ranking path used by generation.</p></div><label className="min-w-56"><span className="text-xs font-medium">Current task</span><select value={taskType} onChange={(e) => setTaskType(e.target.value)} className="mt-1 w-full rounded-xl border bg-background px-3 py-2 text-sm">{TASKS.map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label></div>{routing && <div className="mt-4 space-y-3"><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Required capabilities</p><div className="mt-2 flex flex-wrap gap-1">{(routing.required_capabilities || []).map((x: string) => <Badge key={x}>{x}</Badge>)}</div></div><div className="rounded-xl border p-3"><p className="text-xs font-semibold">Eligible providers / runtime ranking</p>{(routing.candidates || []).length ? <div className="mt-2 space-y-1">{routing.candidates.map((x: any) => <div key={x.provider} className="flex items-center justify-between gap-3 text-xs"><span>#{x.rank} <strong>{x.provider}</strong> · {x.model}</span><Badge tone={x.rank === 1 ? 'good' : 'blue'}>{x.rank === 1 ? 'SELECTED' : 'ELIGIBLE'}</Badge></div>)}</div> : <p className="mt-2 text-xs text-muted-foreground">No eligible provider.</p>}</div><div className="rounded-xl border p-3"><p className="text-xs font-semibold">Excluded providers</p>{(routing.excluded_candidates || []).length ? <div className="mt-2 space-y-1">{routing.excluded_candidates.map((x: any) => <div key={`${x.provider}-${x.reason}`} className="flex justify-between gap-3 text-xs"><span>{x.provider}</span><span className="text-muted-foreground">{x.reason}</span></div>)}</div> : <p className="mt-2 text-xs text-muted-foreground">None.</p>}</div><div className="rounded-xl border p-3 text-xs"><p><strong>Selected provider:</strong> {routing.selected_provider || 'None'}</p><p className="mt-1"><strong>Selected model:</strong> {routing.selected_model || '—'}</p><p className="mt-1 text-muted-foreground"><strong>Ranking:</strong> {routing.ranking_reason}</p></div></div>}</Card>
        <Card title="Fallback routing"><p className="text-sm text-muted-foreground">Fallback can only use providers that remain configured, active, fresh-healthy, task-compatible and policy-eligible. Failed generations are recorded before the next candidate is attempted.</p><div className="mt-4 rounded-xl border p-4 space-y-3 text-sm"><div className="flex justify-between gap-4"><span>Operator-preferred provider</span><strong>{routing?.selected_provider || '—'}</strong></div><div className="flex justify-between gap-4"><span>Eligible fallback candidates</span><span className="text-xs text-muted-foreground">{(routing?.candidates || []).slice(1).map((x: any) => x.provider).join(' → ') || 'None'}</span></div><div className="flex justify-between"><span>Fallback</span><Badge tone={routing?.fallback_enabled === false ? 'warn' : 'good'}>{routing?.fallback_enabled === false ? 'Disabled' : 'Enabled'}</Badge></div></div>{latestTrace && <div className="mt-3 rounded-xl border p-3"><p className="text-xs font-semibold">Latest {taskType} generation trace</p><div className="mt-2 space-y-1 text-xs">{traceAttempts.length ? traceAttempts.map((x: any, i: number) => <div key={`${x.provider}-${i}`} className="flex justify-between gap-3"><span>{i + 1}. {x.provider} / {x.model || '—'}</span><span>{x.status} · {fmtMs(x.latency_ms)}</span></div>) : <span className="text-muted-foreground">No generation attempts recorded.</span>}</div><p className="mt-2 text-[11px] text-muted-foreground">Trace: {latestTrace.trace_id}</p></div>}</Card>
        <Card title="Health / latency / quota"><p className="text-sm text-muted-foreground">Operational health is separate from generation telemetry. Quota/rate-limit signals are shown only when the provider supplies them.</p><div className="mt-4 overflow-x-auto"><table className="w-full text-left text-xs"><thead><tr className="border-b"><th className="px-2 py-2">Provider</th><th className="px-2 py-2">Health</th><th className="px-2 py-2">Last check</th><th className="px-2 py-2">Avg</th><th className="px-2 py-2">P50</th><th className="px-2 py-2">P95</th><th className="px-2 py-2">Failures</th><th className="px-2 py-2">Consecutive</th><th className="px-2 py-2">Quota</th></tr></thead><tbody>{providers.map((p) => { const h = p.health || {}; const fresh = Boolean(p.health_fresh); const quota = h.quota && Object.keys(h.quota).length ? JSON.stringify(h.quota) : 'Not reported'; return <tr key={p.provider} className="border-b last:border-0"><td className="px-2 py-2 font-medium">{p.label}</td><td className="px-2 py-2"><Badge tone={healthTone(p, fresh) as any}>{healthLabel(p, fresh)}</Badge></td><td className="px-2 py-2">{fmtTime(h.checked_at)}</td><td className="px-2 py-2">{fmtMs(h.avg_latency_ms)}</td><td className="px-2 py-2">{fmtMs(h.p50_latency_ms)}</td><td className="px-2 py-2">{fmtMs(h.p95_latency_ms)}</td><td className="px-2 py-2">{h.failed_checks || 0}</td><td className="px-2 py-2">{h.consecutive_failures || 0}</td><td className="max-w-64 truncate px-2 py-2" title={quota}>{quota}</td></tr>; })}</tbody></table></div>{healthError && <p className="mt-3 text-xs text-muted-foreground">{healthError}</p>}</Card>
        <Card title="Runtime execution trace"><p className="text-sm text-muted-foreground">Live execution traces come from the actual Global Intelligence runtime. No artificial countdown is generated.</p>{latestTrace ? <div className="mt-4 space-y-2"><div className="grid gap-2 sm:grid-cols-3"><div className="rounded-xl border p-3"><p className="text-[11px] text-muted-foreground">Run ID</p><p className="mt-1 break-all text-xs font-semibold">{latestTrace.trace_id}</p></div><div className="rounded-xl border p-3"><p className="text-[11px] text-muted-foreground">Status</p><p className="mt-1 text-xs font-semibold">{latestTrace.status}</p></div><div className="rounded-xl border p-3"><p className="text-[11px] text-muted-foreground">Final provider</p><p className="mt-1 text-xs font-semibold">{latestTrace.final_provider || '—'}</p></div></div><div className="max-h-72 overflow-auto rounded-xl border p-3 font-mono text-[11px]">{(latestTrace.events || []).map((x: any, i: number) => <div key={`${x.timestamp}-${i}`} className="border-b py-1 last:border-0"><span className="text-muted-foreground">{fmtTime(x.timestamp)}</span> · <strong>{x.type}</strong> · {x.message}{x.provider ? ` · ${x.provider}` : ''}{x.model ? ` · ${x.model}` : ''}{x.reason ? ` · ${x.reason}` : ''}</div>)}</div></div> : <div className="mt-4 rounded-xl border p-4 text-xs text-muted-foreground">No runtime trace for {taskType} has been recorded in this backend process yet.</div>}</Card>
      </div>
      <Card className="mt-5" title="Routing policy boundary"><div className="space-y-2 text-sm leading-6 text-muted-foreground"><p><strong className="text-foreground">Hard gates:</strong> configured → valid configuration → active → fresh successful health → task compatibility → quota/request policy.</p><p><strong className="text-foreground">Ranking:</strong> eligible providers are ranked by reliability, recent failures, P95 latency, average latency, operator preference, then manual priority. Manual priority cannot override a hard gate.</p><p><strong className="text-foreground">Lifecycle:</strong> NOT CONFIGURED, CONFIGURED, ACTIVE and DEACTIVATED are control states. HEALTHY, STALE, UNHEALTHY and NOT CHECKED are independent health states.</p><p><strong className="text-foreground">Provider isolation:</strong> each adapter owns its model and endpoint semantics. An Ollama model/endpoint cannot be stored or routed as OpenRouter or Gemini configuration.</p></div></Card>
    </CareerOSShell>
  );
}

function currentHealthy(p: Provider) { return Boolean(p.configured && p.configuration_valid !== false && p.health?.status === 'healthy' && p.health_fresh); }
