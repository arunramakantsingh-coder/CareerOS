'use client';

import { useEffect, useMemo, useState } from 'react';
import { CareerOSShell, PageHeader, Card, Badge } from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';

function fmtTime(value?: string) { return value ? new Date(value).toLocaleTimeString() : '—'; }
function fmtMs(value?: number) { return value == null ? '—' : `${Number(value).toFixed(1)} ms`; }

export default function RuntimeDiagnostics() {
  const [data, setData] = useState<any>();
  const [traces, setTraces] = useState<any[]>([]);
  const [selectedTraceId, setSelectedTraceId] = useState('');
  const [selectedTrace, setSelectedTrace] = useState<any>(null);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const [diagnostics, runtime] = await Promise.all([apiClient.get('/api/v1/developer/diagnostics'), apiClient.intelligenceRuntimeTraces(50)]);
      setData(diagnostics);
      const next = runtime.traces || [];
      setTraces(next);
      setSelectedTraceId((current) => current || next[0]?.trace_id || '');
      setError('');
    } catch (e: any) { setError(e.message || 'Unable to load runtime diagnostics'); }
  };

  useEffect(() => { void load(); const timer = window.setInterval(() => void load(), 1000); return () => window.clearInterval(timer); }, []);
  useEffect(() => {
    if (!selectedTraceId) { setSelectedTrace(null); return; }
    const local = traces.find((trace) => trace.trace_id === selectedTraceId);
    if (local) { setSelectedTrace(local); return; }
    apiClient.intelligenceRuntimeTrace(selectedTraceId).then(setSelectedTrace).catch(() => setSelectedTrace(null));
  }, [selectedTraceId, traces]);

  const latest = traces[0];
  const healthTraces = useMemo(() => traces.filter((trace) => trace.task_type === 'provider_health_check'), [traces]);
  const generationTraces = useMemo(() => traces.filter((trace) => trace.task_type !== 'provider_health_check'), [traces]);

  return <CareerOSShell>
    <PageHeader eyebrow="Project Control" title="Runtime Diagnostics" description="Live operational view of the Global Intelligence Engine, provider health scheduler, routing decisions, generation attempts, fallback and CV reconciliation activity." action={<Badge tone={data ? 'good' : 'warn'}>{data ? 'Available' : 'Checking'}</Badge>} />
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {[
        ['Version', data?.version], ['Environment', data?.environment], ['Git branch', data?.git_branch], ['Git commit', data?.git_commit],
      ].map(([label, value]) => <Card key={label as string}><p className="text-xs text-muted-foreground">{label}</p><p className="mt-2 break-all font-semibold">{value || '—'}</p></Card>)}
    </div>
    {error && <div className="mt-4 rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm">{error}</div>}

    <Card className="mt-5" title="Global Intelligence runtime status">
      <div className="grid gap-3 md:grid-cols-4"><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Latest run</p><p className="mt-1 text-sm font-semibold">{latest?.task_type || '—'}</p></div><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Generation traces</p><p className="mt-1 text-sm font-semibold">{generationTraces.length}</p></div><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Health cycles</p><p className="mt-1 text-sm font-semibold">{healthTraces.length}</p></div><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Live polling</p><p className="mt-1 text-sm font-semibold">1 second</p></div></div>
    </Card>

    <Card className="mt-5" title="Execution traces">
      <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
        <div className="space-y-2">{traces.length ? traces.map((trace) => <button key={trace.trace_id} type="button" onClick={() => setSelectedTraceId(trace.trace_id)} className={`w-full rounded-xl border p-3 text-left ${selectedTraceId === trace.trace_id ? 'border-primary bg-primary/5' : 'hover:bg-muted/40'}`}><div className="flex items-center justify-between gap-2"><span className="text-sm font-semibold">{trace.task_type}</span><Badge tone={trace.status === 'completed' ? 'good' : trace.status === 'failed' ? 'warn' : 'blue'}>{trace.status}</Badge></div><p className="mt-1 text-[11px] text-muted-foreground">{fmtTime(trace.started_at)} · {trace.final_provider || 'no provider yet'}</p><p className="mt-1 break-all text-[10px] text-muted-foreground">{trace.trace_id}</p></button>) : <div className="rounded-xl border p-4 text-xs text-muted-foreground">No runtime traces yet.</div>}</div>
        <div>{selectedTrace ? <div><div className="grid gap-3 md:grid-cols-4"><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Task</p><p className="mt-1 text-sm font-semibold">{selectedTrace.task_type}</p></div><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Selected</p><p className="mt-1 text-sm font-semibold">{selectedTrace.selected_provider || '—'}</p></div><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Final</p><p className="mt-1 text-sm font-semibold">{selectedTrace.final_provider || '—'}</p></div><div className="rounded-xl border p-3"><p className="text-xs text-muted-foreground">Total latency</p><p className="mt-1 text-sm font-semibold">{fmtMs(selectedTrace.total_latency_ms)}</p></div></div><div className="mt-3 rounded-xl border p-3"><p className="text-xs font-semibold">Required capabilities</p><div className="mt-2 flex flex-wrap gap-1">{(selectedTrace.required_capabilities || []).map((cap: string) => <Badge key={cap}>{cap}</Badge>)}</div><p className="mt-3 text-xs text-muted-foreground"><strong>Ranking:</strong> {selectedTrace.ranking_reason || '—'}</p></div><div className="mt-3 rounded-xl border p-3"><p className="text-xs font-semibold">Candidates</p><div className="mt-2 space-y-1 text-xs">{(selectedTrace.candidates || []).map((x: any) => <div key={`${x.provider}-${x.rank}`} className="flex justify-between gap-3"><span>#{x.rank} {x.provider} / {x.model}</span><span>{x.reason}</span></div>)}</div></div><div className="mt-3 rounded-xl border p-3"><p className="text-xs font-semibold">Excluded candidates</p><div className="mt-2 space-y-1 text-xs">{(selectedTrace.excluded_candidates || []).map((x: any) => <div key={`${x.provider}-${x.reason}`} className="flex justify-between gap-3"><span>{x.provider}</span><span className="text-muted-foreground">{x.reason}</span></div>)}</div></div><div className="mt-3 max-h-[420px] overflow-auto rounded-xl border p-3 font-mono text-[11px]">{(selectedTrace.events || []).map((event: any, index: number) => <div key={`${event.timestamp}-${index}`} className="border-b py-1 last:border-0"><span className="text-muted-foreground">{fmtTime(event.timestamp)}</span> · <strong>{event.type}</strong> · {event.message}{event.provider ? ` · ${event.provider}` : ''}{event.model ? ` · ${event.model}` : ''}{event.reason ? ` · ${event.reason}` : ''}</div>)}</div></div> : <div className="rounded-xl border p-6 text-sm text-muted-foreground">Select a trace to inspect the actual runtime decisions.</div>}</div>
      </div>
    </Card>

    <Card className="mt-5" title="Runtime trace contract">
      <pre className="overflow-auto rounded-xl border bg-muted/20 p-4 text-xs">{JSON.stringify({ task_type: selectedTrace?.task_type, required_capabilities: selectedTrace?.required_capabilities, candidates: selectedTrace?.candidates, excluded_candidates: selectedTrace?.excluded_candidates, selected_provider: selectedTrace?.selected_provider, selected_model: selectedTrace?.selected_model, ranking_reason: selectedTrace?.ranking_reason, attempts: selectedTrace?.attempts, fallback_used: selectedTrace?.fallback_used, final_provider: selectedTrace?.final_provider, total_latency_ms: selectedTrace?.total_latency_ms }, null, 2)}</pre>
    </Card>
  </CareerOSShell>;
}
