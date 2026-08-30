'use client';

import { useEffect, useMemo, useState } from 'react';
import { CareerOSShell, Badge, Button, Card, PageHeader } from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';

type Guidance = {
  suggested_structure?: string[];
  evidence?: string[];
  warning?: string;
};

const demoTranscript = [
  { speaker: 'Interviewer', text: 'Can you explain the BGP best path selection process?', time: '00:42' },
  { speaker: 'You', text: 'I normally start with the highest-priority attributes and work down the sequence.', time: '00:51' },
];

const demoAnswer = [
  ['Weight', 'Highest wins — Cisco local'],
  ['Local Preference', 'Highest wins — AS-wide'],
  ['Locally Originated', 'Preferred'],
  ['AS Path', 'Shortest wins'],
  ['Origin', 'IGP > EGP > Incomplete'],
  ['MED', 'Lowest wins'],
  ['Path Type', 'eBGP > iBGP'],
  ['IGP Metric', 'Lowest to next hop'],
  ['Age', 'Oldest eBGP path'],
  ['Router ID', 'Lowest wins'],
  ['Cluster List', 'Shortest wins'],
  ['Neighbor IP', 'Lowest wins'],
];

export default function LiveInterview() {
  const [apps, setApps] = useState<any[]>([]);
  const [appId, setAppId] = useState('');
  const [session, setSession] = useState<any>();
  const [question, setQuestion] = useState('');
  const [guidance, setGuidance] = useState<Guidance>();
  const [msg, setMsg] = useState('');
  const [showEvidence, setShowEvidence] = useState(true);
  const [demo, setDemo] = useState(true);

  useEffect(() => {
    apiClient.applications().then(setApps).catch(e => setMsg(e.message));
  }, []);

  const status = useMemo(() => session ? 'SESSION READY' : 'READY', [session]);

  const start = async () => {
    if (!appId) {
      setMsg('Select an application first.');
      return;
    }
    setMsg('');
    try {
      setSession(await apiClient.startLive({ application_id: appId }));
      setGuidance(undefined);
      setDemo(false);
    } catch (e: any) {
      setMsg(e.message);
    }
  };

  const assist = async () => {
    if (!session || !question.trim()) return;
    setMsg('');
    try {
      setGuidance(await apiClient.assistLive(session.id, question.trim()));
      setQuestion('');
    } catch (e: any) {
      setMsg(e.message);
    }
  };

  return (
    <CareerOSShell>
      <PageHeader
        eyebrow="Live Interview Workspace"
        title="Interview command center"
        description="A focused workspace for transcript review and concise, evidence-aware guidance when AI assistance is explicitly permitted by the interview or assessment."
        action={<div className="flex items-center gap-2"><Badge tone={session ? 'good' : 'muted'}>{status}</Badge><Button onClick={start}>Start session</Button></div>}
      />

      <div className="mb-5 grid gap-3 md:grid-cols-[1fr_auto]">
        <div className="rounded-xl border border-primary/20 bg-primary/5 px-4 py-3 text-sm text-muted-foreground">
          <strong className="text-foreground">Permission-aware mode:</strong> use AI assistance only where the interviewer explicitly allows it. CareerOS keeps responses concise and grounded in available evidence.
        </div>
        <button onClick={() => setDemo(v => !v)} className="rounded-xl border bg-card px-4 py-3 text-xs font-semibold hover:bg-muted">
          {demo ? 'Hide demo' : 'Show format demo'}
        </button>
      </div>

      {msg && <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-700 dark:text-red-300">{msg}</div>}

      <div className="grid gap-4 xl:grid-cols-[280px_minmax(0,1fr)_390px]">
        <Card title="Session control">
          <div className="space-y-4">
            <select value={appId} onChange={e => setAppId(e.target.value)} className="w-full rounded-lg border bg-background px-3 py-2.5 text-sm">
              <option value="">Select application</option>
              {apps.map(a => <option key={a.id} value={a.id}>{a.advertised_title} · {a.company || '—'}</option>)}
            </select>

            <div className="rounded-xl border bg-muted/20 p-4">
              <div className="flex items-center justify-between"><span className="text-xs uppercase tracking-[.14em] text-muted-foreground">Session</span><span className="font-mono text-xs">{session?.id ? String(session.id).slice(0, 12) : '—'}</span></div>
              <div className="mt-4 flex items-center gap-3"><span className={`grid h-10 w-10 place-items-center rounded-full ${session ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}>◉</span><div><p className="text-sm font-semibold">{session ? 'Workspace active' : 'Not started'}</p><p className="text-xs text-muted-foreground">{session ? 'Question assistance available' : 'Select an application'}</p></div></div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-muted-foreground">Career evidence</span><Badge tone="blue">Ready</Badge></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Knowledge layer</span><Badge tone="blue">Ready</Badge></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Answer style</span><span className="font-medium">One-line</span></div>
            </div>
          </div>
        </Card>

        <Card title="Conversation transcript">
          <div className="space-y-3">
            {(demo ? demoTranscript : []).map((item, index) => (
              <div key={index} className={`rounded-xl border p-4 ${item.speaker === 'Interviewer' ? 'border-primary/20 bg-primary/5' : 'bg-muted/20'}`}>
                <div className="flex items-center justify-between gap-3"><span className="text-xs font-semibold uppercase tracking-[.12em] text-muted-foreground">{item.speaker}</span><span className="font-mono text-[11px] text-muted-foreground">{item.time}</span></div>
                <p className="mt-2 text-sm leading-6">{item.text}</p>
              </div>
            ))}
            <div className="rounded-xl border border-dashed p-5 text-center">
              <p className="text-sm font-medium">Transcript stream</p>
              <p className="mt-1 text-xs text-muted-foreground">A permitted transcription source can feed this area in a later integration. No microphone capture is enabled by this UI-only milestone.</p>
            </div>
          </div>
        </Card>

        <Card title="Concise answer panel">
          {demo ? (
            <div className="rounded-xl border border-primary/25 bg-primary/5 p-4">
              <div className="flex items-start justify-between gap-3"><div><p className="text-[11px] font-semibold uppercase tracking-[.14em] text-primary">Detected topic · demo</p><h2 className="mt-1 text-lg font-bold">BGP Best Path</h2></div><Badge tone="blue">Technical</Badge></div>
              <div className="mt-4 space-y-2">{demoAnswer.map(([label, value], index) => <div key={label} className="grid grid-cols-[22px_1fr] gap-2 text-sm"><span className="font-mono text-xs text-muted-foreground">{index + 1}.</span><p><strong>{label}:</strong> {value}</p></div>)}</div>
              <div className="mt-4 border-t pt-3 text-xs text-muted-foreground">Format: indicative · one-line · high-signal</div>
            </div>
          ) : guidance ? (
            <div className="space-y-4">
              <Badge tone="blue">Evidence-first guidance</Badge>
              <div><p className="text-xs font-semibold uppercase tracking-[.14em] text-muted-foreground">Suggested structure</p><ol className="mt-2 list-decimal space-y-1 pl-5 text-sm">{guidance.suggested_structure?.map((x, n) => <li key={n}>{x}</li>)}</ol></div>
              <div><p className="text-xs font-semibold uppercase tracking-[.14em] text-muted-foreground">Relevant evidence</p>{guidance.evidence?.length ? <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">{guidance.evidence.map((x, n) => <li key={n}>{x}</li>)}</ul> : <p className="mt-2 text-sm text-muted-foreground">No directly matching evidence found.</p>}</div>
              {guidance.warning && <p className="rounded-lg bg-amber-500/10 p-3 text-xs text-amber-700 dark:text-amber-300">{guidance.warning}</p>}
            </div>
          ) : <div className="rounded-xl border border-dashed p-6 text-center"><p className="text-sm font-medium">No answer card yet</p><p className="mt-1 text-xs text-muted-foreground">Enter a question below to request structured, evidence-aware guidance.</p></div>}

          <div className="mt-4 border-t pt-4">
            <label className="text-xs font-semibold uppercase tracking-[.14em] text-muted-foreground">Question / transcript input</label>
            <textarea value={question} onChange={e => setQuestion(e.target.value)} rows={4} placeholder="Enter the question or permitted transcript text…" className="mt-2 w-full rounded-lg border bg-background px-3 py-2.5 text-sm" />
            <div className="mt-2 flex items-center justify-between gap-3"><label className="flex items-center gap-2 text-xs text-muted-foreground"><input type="checkbox" checked={showEvidence} onChange={e => setShowEvidence(e.target.checked)} /> Show evidence</label><Button onClick={assist} disabled={!session || !question.trim()}>Generate guidance</Button></div>
            {showEvidence && <p className="mt-2 text-[11px] text-muted-foreground">Evidence references remain visible so career claims can be checked against CareerOS data.</p>}
          </div>
        </Card>
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-3">
        <Card title="Question intelligence"><p className="text-sm text-muted-foreground">Keep topic and intent visible without flooding the workspace with conversational AI text.</p></Card>
        <Card title="CareerOS evidence"><p className="text-sm text-muted-foreground">Use verified profile, experience, certification and Career Vault information as the grounding layer.</p></Card>
        <Card title="Private notes"><textarea className="min-h-24 w-full rounded-lg border bg-background px-3 py-2 text-sm" placeholder="Your notes…" /></Card>
      </div>
    </CareerOSShell>
  );
}
