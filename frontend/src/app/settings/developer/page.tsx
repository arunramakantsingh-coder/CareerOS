'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { CareerOSShell, Card, PageHeader, Button, Badge } from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';

type DeveloperStatus = { tools?: string[]; developer_mode?: boolean; role?: string; email?: string; reset_scopes?: string[] };
type Diagnostics = { version?: string; git_commit?: string; git_branch?: string; environment?: string; profile_present?: boolean; github_repository?: string };
type ResetResponse = { scope?: string; documents_removed?: number; evidence_removed?: number; personas_removed?: number; gmail_tokens_cleared?: number; connector_accounts_removed?: number };

const resetOptions = [
  ['career_data', 'Career data', 'Clear parsed profile facts and evidence links.'],
  ['documents', 'Documents', 'Remove uploaded test documents from CareerOS storage.'],
  ['personas', 'Personas', 'Clear generated persona suggestions and personas.'],
  ['connections', 'Connections', 'Clear test connector records and Gmail mailbox tokens while preserving Google sign-in.'],
  ['all', 'Everything', 'Return the developer account to a clean onboarding test state.'],
] as const;

export default function DeveloperMode() {
  const [status, setStatus] = useState<DeveloperStatus | null>(null);
  const [diagnostics, setDiagnostics] = useState<Diagnostics | null>(null);
  const [msg, setMsg] = useState('');
  const [busy, setBusy] = useState(false);
  const [scope, setScope] = useState('all');

  useEffect(() => {
    Promise.all([
      apiClient.get<DeveloperStatus>('/api/v1/developer/status'),
      apiClient.get<Diagnostics>('/api/v1/developer/diagnostics'),
    ])
      .then(([s, d]) => { setStatus(s); setDiagnostics(d); })
      .catch((e: any) => setMsg(e.message || 'Developer access denied'));
  }, []);

  const reset = async () => {
    const label = resetOptions.find(([key]) => key === scope)?.[1] || 'test data';
    if (!confirm(`Reset ${label.toLowerCase()} for your CareerOS developer account? Your login account will be preserved.`)) return;
    setBusy(true);
    setMsg('');
    try {
      const r = await apiClient.post<ResetResponse>('/api/v1/developer/reset', { scope });
      setMsg(`Reset complete: ${r.scope}. Documents removed: ${r.documents_removed || 0}; evidence removed: ${r.evidence_removed || 0}; personas removed: ${r.personas_removed || 0}. Login preserved.`);
    } catch (e: any) {
      setMsg(e.message || 'Reset failed');
    } finally {
      setBusy(false);
    }
  };

  if (!status) {
    return <CareerOSShell><div className="grid min-h-[50vh] place-items-center text-sm text-muted-foreground">{msg || 'Checking Developer Mode…'}</div></CareerOSShell>;
  }

  return <CareerOSShell>
    <PageHeader
      eyebrow="Project Control"
      title="Developer Mode"
      description="A small control layer for development, testing and recovery. It does not duplicate product features."
      action={<Badge tone="good">Authorized developer</Badge>}
    />

    <div className="grid gap-5 lg:grid-cols-2">
      <Card title="Project & change control" className="techno-glow">
        <div className="grid gap-3 sm:grid-cols-2">
          <Link href="/project-tracker" className="rounded-xl border p-4 transition hover:border-primary/40 hover:bg-muted/30"><p className="font-semibold">Project Tracker</p><p className="mt-1 text-xs text-muted-foreground">Milestones, current stage and safety gates.</p></Link>
          <Link href="/bug-tracker" className="rounded-xl border p-4 transition hover:border-primary/40 hover:bg-muted/30"><p className="font-semibold">Bug Tracker</p><p className="mt-1 text-xs text-muted-foreground">Cross-module issues and known limitations.</p></Link>
          <a href="https://github.com/arunramakantsingh-coder/CareerOS/commits" target="_blank" rel="noreferrer" className="rounded-xl border p-4 transition hover:border-primary/40 hover:bg-muted/30"><p className="font-semibold">Version / Git History</p><p className="mt-1 text-xs text-muted-foreground">Commits, branches and recovery points live in GitHub.</p></a>
          <a href="https://github.com/arunramakantsingh-coder/CareerOS/issues" target="_blank" rel="noreferrer" className="rounded-xl border p-4 transition hover:border-primary/40 hover:bg-muted/30"><p className="font-semibold">GitHub Issues</p><p className="mt-1 text-xs text-muted-foreground">Use the repository as the source of truth for bugs and work items.</p></a>
        </div>
      </Card>

      <Card title="Testing & recovery">
        <p className="text-sm leading-6 text-muted-foreground">Use one generic reset mechanism instead of building a separate developer page for every future module. Individual product pages can call the same scoped reset when Developer Mode is enabled.</p>
        <div className="mt-4 space-y-3">
          <select value={scope} onChange={e => setScope(e.target.value)} className="w-full rounded-xl border bg-background px-3 py-2.5 text-sm">
            {resetOptions.map(([key, label]) => <option key={key} value={key}>{label}</option>)}
          </select>
          <Button onClick={reset} disabled={busy}>{busy ? 'Resetting…' : 'Reset selected test data'}</Button>
        </div>
        <p className="mt-3 text-xs text-muted-foreground">Destructive actions require confirmation, are scoped to this authenticated developer, are audit logged, and never delete the login account.</p>
      </Card>
    </div>

    <div className="mt-5 grid gap-5 lg:grid-cols-2">
      <Card title="Runtime diagnostics">
        <div className="grid gap-3 text-sm sm:grid-cols-2">
          <div><p className="text-xs text-muted-foreground">Version</p><p className="mt-1 font-semibold">{diagnostics?.version || 'development'}</p></div>
          <div><p className="text-xs text-muted-foreground">Environment</p><p className="mt-1 font-semibold">{diagnostics?.environment || 'development'}</p></div>
          <div><p className="text-xs text-muted-foreground">Git branch</p><p className="mt-1 break-all font-semibold">{diagnostics?.git_branch || 'unknown'}</p></div>
          <div><p className="text-xs text-muted-foreground">Git commit</p><p className="mt-1 break-all font-semibold">{diagnostics?.git_commit || 'unknown'}</p></div>
        </div>
      </Card>

      <Card title="Recovery boundary">
        <div className="space-y-2 text-sm text-muted-foreground">
          <p>• GitHub is the code/version source of truth.</p>
          <p>• Successful stages should be committed as recovery points.</p>
          <p>• Rollback means selecting a known Git commit/branch; Developer Mode does not silently rewrite Git history.</p>
          <p>• GitHub branch protection, reviews and Actions remain the safer place for repository-level controls.</p>
        </div>
        {diagnostics?.github_repository && <a className="mt-4 inline-block text-sm font-semibold text-primary" href={diagnostics.github_repository} target="_blank" rel="noreferrer">Open CareerOS repository →</a>}
      </Card>
    </div>

    {msg && <div className="mt-4 rounded-xl border bg-card px-4 py-3 text-sm">{msg}</div>}
  </CareerOSShell>;
}
