'use client';

import Link from 'next/link';
import { CareerOSShell, PageHeader, Badge } from '@/components/CareerOSShell';

const cards = [
  ['Project Tracker', 'Module sequencing, milestones, implementation status and verification gates.', '/project-tracker', '▥'],
  ['Bug Tracker', 'Single cross-module record for defects, regressions and fixes.', '/bug-tracker', '⚠'],
  ['Roadmap', 'Planned releases, dependencies and controlled progression.', '/roadmap', '➜'],
  ['Runtime Diagnostics', 'Backend, database, authentication and application runtime health.', '/project-control/runtime-diagnostics', '◉'],
  ['Intelligence Engine', 'Local/provider-neutral AI gateway, capabilities and model runtime status.', '/project-control/intelligence', '✦'],
  ['Test Data & Reset', 'Safe scoped test-data controls and the master developer reset.', '/project-control/test-data', '↻'],
  ['Processing / Jobs', 'Background processing visibility and future job execution controls.', '/project-control/processing', '⚙'],
  ['Version & Git History', 'Branches, commits, baselines and known recovery points.', '/project-control/version', '◇'],
  ['Change History', 'What changed, why it changed, affected areas and verification evidence.', '/project-control/history', '≡'],
  ['Rollback & Recovery', 'Compare recovery points and prepare an explicit Git-based rollback.', '/project-control/rollback', '↶'],
] as const;

export default function ProjectControl() {
  return <CareerOSShell><PageHeader eyebrow="Developer Only" title="Project Control" description="One controlled workspace for CareerOS development, testing, diagnostics, intelligence, version history and recovery. Normal users do not see or access this area." action={<Badge tone="good">Developer access</Badge>} /><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{cards.map(([title, description, href, icon]) => <Link key={href} href={href} className="group rounded-2xl border bg-card p-5 shadow-sm transition duration-200 hover:-translate-y-1 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/10 focus:outline-none focus:ring-2 focus:ring-primary/40"><div className="flex items-start justify-between gap-4"><span className="grid h-11 w-11 place-items-center rounded-xl bg-primary/10 text-lg text-primary transition group-hover:bg-primary group-hover:text-primary-foreground">{icon}</span><span className="text-muted-foreground transition group-hover:translate-x-1 group-hover:text-primary">→</span></div><h2 className="mt-5 text-base font-bold">{title}</h2><p className="mt-2 text-sm leading-6 text-muted-foreground">{description}</p><p className="mt-5 text-xs font-semibold uppercase tracking-[.14em] text-primary">Open workspace</p></Link>)}</div><div className="mt-6 rounded-2xl border bg-card/60 p-5"><p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">Boundary</p><p className="mt-2 text-sm leading-6 text-muted-foreground">Project Control is the single home for developer tooling. Product areas such as Profile, Connections, Opportunity and Interview remain normal CareerOS workspaces; developer tooling is not duplicated inside them.</p></div></CareerOSShell>;
}
