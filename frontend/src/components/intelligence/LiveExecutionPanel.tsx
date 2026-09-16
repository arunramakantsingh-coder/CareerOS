'use client';

import { ReactNode } from 'react';
import { Badge } from '@/components/CareerOSShell';

type Stage = { key: string; label: string };
type RuntimeEvent = { timestamp?: string; type?: string; message?: string; provider?: string; model?: string; reason?: string; chars?: number; latency_ms?: number; [key: string]: unknown };

type LiveExecutionPanelProps = {
  title: string;
  subject?: string;
  jobId?: string;
  status: string;
  stage: string;
  progress: number;
  operation: string;
  message?: string;
  provider?: string | null;
  model?: string | null;
  jobElapsedSeconds: number;
  runtimeElapsedSeconds: number;
  activityAgeSeconds?: number | null;
  timeoutSeconds?: number;
  remainingSeconds?: number | null;
  output?: string;
  outputChars?: number;
  outputRate?: number;
  thinkingAvailable?: boolean;
  thinkingText?: string;
  thinkingChars?: number;
  providerMetrics?: Record<string, unknown>;
  events?: RuntimeEvent[];
  stages: Stage[];
  runtimeStatus?: string;
  failure?: string;
  completedMessage?: string;
  headerActions?: ReactNode;
};

const duration = (seconds: number) => {
  const s = Math.max(0, Math.floor(seconds));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  return h ? `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}` : `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
};
const fmtTime = (value?: string) => value ? new Date(value).toLocaleTimeString() : '—';
const fmtMs = (value: unknown) => value == null ? '—' : `${(Number(value) / 1000000).toFixed(1)} ms`;
const eventLabel = (type?: string) => ({
  GENERATION_DELTA: 'Model is generating structured output',
  GENERATION_STARTED: 'Model generation started',
  GENERATION_COMPLETED: 'Model generation completed',
  GENERATION_FAILED: 'Model generation failed',
  PROVIDER_STREAM_STARTED: 'Provider stream connected',
  PROVIDER_SELECTED: 'AI provider selected',
  PROVIDER_EXCLUDED: 'Provider excluded by routing',
  PROVIDER_ELIGIBLE: 'Provider eligible for execution',
  TASK_IDENTIFIED: 'Task identified',
  HEALTH_GATE: 'Provider health gate checked',
  ROUTING_FAILED: 'Routing failed',
  ROUTING_STARTED: 'Routing started',
  ROUTING_COMPLETED: 'Routing completed',
  THINKING_DELTA: 'Provider thinking received',
} as Record<string, string>)[type || ''] || type || 'Runtime activity';

export default function LiveExecutionPanel({
  title, subject, jobId, status, stage, progress, operation, message, provider, model,
  jobElapsedSeconds, runtimeElapsedSeconds, activityAgeSeconds, timeoutSeconds = 0, remainingSeconds,
  output, outputChars = 0, outputRate = 0, thinkingAvailable = false, thinkingText = '', thinkingChars = 0,
  providerMetrics = {}, events = [], stages, runtimeStatus = 'waiting', failure, completedMessage,
  headerActions,
}: LiveExecutionPanelProps) {
  const doneStatus = status === 'completed';
  const failedStatus = status === 'failed';
  const streamActive = !failedStatus && !doneStatus && events.at(-1)?.type === 'GENERATION_DELTA' && (activityAgeSeconds == null || activityAgeSeconds < 5);
  const statusTone = failedStatus ? 'warn' : doneStatus ? 'good' : streamActive ? 'good' : 'blue';
  const timerLabel = doneStatus ? 'Completed' : failedStatus ? 'Stopped' : duration(jobElapsedSeconds);
  const hasRuntime = Boolean(provider || model || events.length || Object.keys(providerMetrics).length || outputChars || thinkingChars);
  const currentIndex = stages.findIndex(item => item.key === stage);
  const failedIndex = failedStatus ? stages.findIndex(item => item.key === stage) : -1;
  const native = providerMetrics;

  return <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-[2px]">
    <div className="flex max-h-[94vh] w-full max-w-[1500px] flex-col overflow-hidden rounded-2xl border bg-background shadow-2xl">
      <div className="shrink-0 border-b p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <p className="text-xs font-semibold uppercase tracking-[.14em] text-primary">CareerOS Global Intelligence · Live execution</p>
            <h2 className="mt-1 text-xl font-semibold">{title}</h2>
            <p className="mt-1 truncate text-sm text-muted-foreground">{subject || 'AI task'}{jobId ? ` · job ${jobId.slice(0, 8)}` : ''}</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="rounded-xl border bg-background/60 px-4 py-2 text-right">
              <p className="text-[10px] uppercase tracking-[.12em] text-muted-foreground">Job timer</p>
              <p className="font-mono text-2xl font-bold tabular-nums">{timerLabel}</p>
            </div>
            {headerActions}
          </div>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-4">
          <div className="rounded-xl border bg-background/30 p-3"><p className="text-[10px] uppercase tracking-[.12em] text-muted-foreground">Current stage</p><p className="mt-1 text-sm font-semibold capitalize">{stage.replaceAll('_', ' ')}</p><p className="mt-1 text-xs text-muted-foreground">{progress}% complete</p></div>
          <div className="rounded-xl border bg-background/30 p-3"><p className="text-[10px] uppercase tracking-[.12em] text-muted-foreground">Current operation</p><p className="mt-1 text-sm font-semibold">{operation}</p><p className="mt-1 truncate text-xs text-muted-foreground">{message || (streamActive ? 'Receiving provider stream' : 'Based on latest runtime event')}</p></div>
          <div className="rounded-xl border bg-background/30 p-3"><p className="text-[10px] uppercase tracking-[.12em] text-muted-foreground">AI runtime</p><p className="mt-1 text-sm font-semibold">{hasRuntime ? `${provider || 'provider pending'}${model ? ` · ${model}` : ''}` : 'Trace not visible yet'}</p><p className="mt-1 text-xs text-muted-foreground">Generation {runtimeElapsedSeconds ? duration(runtimeElapsedSeconds) : '—'}</p></div>
          <div className="rounded-xl border bg-background/30 p-3"><p className="text-[10px] uppercase tracking-[.12em] text-muted-foreground">Last activity</p><p className="mt-1 text-sm font-semibold">{activityAgeSeconds == null ? '—' : activityAgeSeconds < 2 ? 'Just now' : `${Math.floor(activityAgeSeconds)}s ago`}</p><p className="mt-1 text-xs text-muted-foreground">{events.length} runtime events</p></div>
        </div>
        <div className="mt-4 flex items-center gap-3"><div className="h-2 flex-1 overflow-hidden rounded-full bg-muted"><div className="h-full bg-primary transition-all duration-500" style={{ width: `${Math.min(100, Math.max(0, progress))}%` }} /></div><span className="w-10 text-right text-xs font-semibold tabular-nums text-muted-foreground">{progress}%</span></div>
      </div>

      <div className="grid min-h-0 flex-1 grid-cols-1 gap-5 overflow-y-auto p-5 lg:grid-cols-[minmax(300px,.72fr)_minmax(0,1.28fr)]">
        <div className="space-y-4">
          <div className="rounded-xl border p-4">
            <div className="flex items-center justify-between"><p className="text-xs font-semibold uppercase tracking-[.12em]">Pipeline</p><Badge tone={statusTone}>{status}</Badge></div>
            <div className="mt-4 space-y-3">
              {stages.map((item, index) => {
                const done = doneStatus || (currentIndex >= 0 && index < currentIndex);
                const current = !doneStatus && !failedStatus && item.key === stage;
                const failed = failedStatus && (item.key === stage || index === failedIndex);
                return <div key={item.key} className="flex items-start gap-3">
                  <div className={`mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full border text-xs ${done ? 'bg-primary text-primary-foreground' : failed ? 'border-destructive bg-destructive/10 text-destructive' : current ? 'border-primary bg-primary/10 text-primary' : 'bg-muted'}`}>{done ? '✓' : failed ? '!' : current ? '●' : ''}</div>
                  <div className="min-w-0 flex-1"><div className={`text-sm font-medium ${failed ? 'text-destructive' : ''}`}>{item.label}</div>{current && <p className="mt-0.5 text-xs text-muted-foreground">{message || operation}</p>}{failed && <p className="mt-0.5 text-xs text-destructive">{failure || 'Failed at this stage.'}</p>}</div>{current && <span className="text-xs font-semibold tabular-nums text-muted-foreground">{progress}%</span>}
                </div>;
              })}
            </div>
          </div>

          <div className="rounded-xl border p-4">
            <div className="flex items-center justify-between"><p className="text-xs font-semibold uppercase tracking-[.12em]">Execution telemetry</p><Badge tone={runtimeStatus === 'completed' ? 'good' : runtimeStatus === 'failed' ? 'warn' : streamActive ? 'good' : 'blue'}>{runtimeStatus}</Badge></div>
            <div className="mt-3 grid gap-2 sm:grid-cols-2">
              <div className="rounded-lg border p-3"><p className="text-[10px] text-muted-foreground">Provider</p><p className="mt-1 text-xs font-semibold">{provider || 'Selecting…'}</p></div>
              <div className="rounded-lg border p-3"><p className="text-[10px] text-muted-foreground">Model</p><p className="mt-1 text-xs font-semibold">{model || 'Selecting…'}</p></div>
              <div className="rounded-lg border p-3"><p className="text-[10px] text-muted-foreground">Job elapsed</p><p className="mt-1 font-mono text-xs font-semibold tabular-nums">{duration(jobElapsedSeconds)}</p></div>
              <div className="rounded-lg border p-3"><p className="text-[10px] text-muted-foreground">Generation elapsed</p><p className="mt-1 font-mono text-xs font-semibold tabular-nums">{duration(runtimeElapsedSeconds)}</p></div>
              <div className="rounded-lg border p-3"><p className="text-[10px] text-muted-foreground">Output</p><p className="mt-1 text-xs font-semibold">{outputChars.toLocaleString()} chars · {outputRate.toFixed(1)} chars/s</p></div>
              <div className="rounded-lg border p-3"><p className="text-[10px] text-muted-foreground">Fallback</p><p className="mt-1 text-xs font-semibold">{hasRuntime ? 'No' : '—'}</p></div>
            </div>
            {timeoutSeconds > 0 && <div className={`mt-3 rounded-lg border p-3 ${remainingSeconds != null && remainingSeconds < 30 ? 'border-amber-500/40 bg-amber-500/5' : ''}`}><div className="flex items-center justify-between"><span className="text-xs font-semibold">Configured generation timeout</span><span className="font-mono text-xs font-semibold tabular-nums">{remainingSeconds == null ? '—' : `${Math.floor(remainingSeconds)}s remaining`}</span></div><p className="mt-1 text-[11px] text-muted-foreground">Actual configured timeout; not a simulated progress countdown.</p></div>}
            {Object.keys(native).length > 0 && <div className="mt-3 grid gap-2 sm:grid-cols-2"><div className="rounded-lg border p-2"><p className="text-[10px] text-muted-foreground">Total duration</p><p className="mt-1 text-xs font-semibold">{fmtMs(native.total_duration)}</p></div><div className="rounded-lg border p-2"><p className="text-[10px] text-muted-foreground">Model load</p><p className="mt-1 text-xs font-semibold">{fmtMs(native.load_duration)}</p></div><div className="rounded-lg border p-2"><p className="text-[10px] text-muted-foreground">Prompt evaluation</p><p className="mt-1 text-xs font-semibold">{fmtMs(native.prompt_eval_duration)} · {native.prompt_eval_count ?? '—'} tokens</p></div><div className="rounded-lg border p-2"><p className="text-[10px] text-muted-foreground">Generation evaluation</p><p className="mt-1 text-xs font-semibold">{fmtMs(native.eval_duration)} · {native.eval_count ?? '—'} tokens</p></div></div>}
          </div>
        </div>

        <div className="grid min-h-0 gap-4 lg:grid-rows-[minmax(300px,1fr)_minmax(260px,1fr)]">
          <div className="flex min-h-0 flex-col rounded-xl border p-4">
            <div className="flex items-center justify-between gap-3"><div><p className="text-xs font-semibold uppercase tracking-[.12em]">Live generation output</p><p className="mt-0.5 text-[10px] text-muted-foreground">Provider output is shown as it arrives; no simulated content.</p></div><div className="flex items-center gap-3 text-xs text-muted-foreground"><span>{outputChars.toLocaleString()} chars</span><span>{outputRate.toFixed(1)} chars/s</span></div></div>
            {thinkingAvailable && <div className="mt-3 rounded-lg border border-primary/20 bg-primary/5 p-3"><div className="flex items-center justify-between"><p className="text-[10px] font-semibold uppercase tracking-[.12em] text-primary">Provider-native thinking</p><span className="text-[10px] text-muted-foreground">{thinkingChars.toLocaleString()} chars</span></div><pre className="mt-2 max-h-28 overflow-auto whitespace-pre-wrap font-mono text-[10px] leading-4">{thinkingText || 'Thinking stream active; waiting for content…'}</pre></div>}
            <div className="mt-3 min-h-0 flex-1 overflow-auto rounded-lg border bg-black/10 p-4"><pre className="min-h-full whitespace-pre-wrap break-words font-mono text-xs leading-5">{output || <span className="text-muted-foreground">Waiting for provider output…</span>}</pre></div>
          </div>

          <div className="flex min-h-0 flex-col rounded-xl border p-4">
            <div className="flex items-center justify-between gap-3"><div><p className="text-xs font-semibold uppercase tracking-[.12em]">Live event stream</p><p className="mt-0.5 text-[10px] text-muted-foreground">Newest event at bottom · actual runtime telemetry</p></div><Badge tone={streamActive ? 'good' : 'muted'}>{streamActive ? 'streaming' : `${events.length} events`}</Badge></div>
            <div className="mt-3 min-h-0 flex-1 overflow-auto rounded-lg border bg-black/10 p-2 font-mono text-[10px]">{events.length ? events.map((event, index) => <div key={`${event.timestamp}-${index}`} className="border-b py-2 last:border-0"><div className="flex flex-wrap gap-x-2 gap-y-0.5"><span className="text-muted-foreground">{fmtTime(event.timestamp)}</span><strong className="text-primary">{event.type}</strong><span className="text-muted-foreground">{eventLabel(event.type)}</span></div><div className="mt-0.5 break-words">{event.message}{event.provider ? ` · ${event.provider}` : ''}{event.model ? ` · ${event.model}` : ''}{event.reason ? ` · ${event.reason}` : ''}{event.chars != null ? ` · ${event.chars} chars` : ''}{event.latency_ms != null ? ` · ${Number(event.latency_ms).toFixed(1)} ms` : ''}</div></div>) : <div className="p-4 text-muted-foreground">No runtime events have been published yet.</div>}</div>
          </div>
        </div>
      </div>

      {failedStatus && <div className="shrink-0 border-t border-destructive/20 bg-destructive/5 px-5 py-4 text-sm text-destructive"><strong>Failure detected:</strong> {failure || `Task failed during ${stage.replaceAll('_', ' ')}.`}</div>}
      {doneStatus && <div className="shrink-0 border-t bg-muted/20 px-5 py-4 text-sm">{completedMessage || 'Completed.'}</div>}
    </div>
  </div>;
}
