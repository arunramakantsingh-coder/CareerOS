'use client';
import Link from 'next/link';
import { CareerOSShell, Card, PageHeader, Badge } from '@/components/CareerOSShell';
const bugs=[
 ['BUG-001','Documents upload error renders validation object','Document intake','fixed','React error boundary was receiving FastAPI validation arrays instead of a string'],
 ['BUG-002','CV intake and bulk vault were visually/semantically mixed','Documents','fixed','Dedicated CV intake and separate bulk evidence vault restored'],
 ['BUG-003','Horizontal navigation duplicated sidebar modules','Shell','fixed','Horizontal strip now represents career journey; sidebar remains module navigation'],
 ['BUG-004','Camera capture unreliable on mobile/LAN HTTP','Documents','mitigated','Scanner now detects secure-context support and provides camera/file fallback'],
 ['BUG-005','OAuth buttons existed without usable provider configuration feedback','Authentication','in review','Backend routes exist; runtime requires provider credentials/callback configuration'],
 ['BUG-006','Profile builder incomplete for manual editing','Profile','fixed in this milestone','Unified editable personal, experience, education, certification and skills builder'],
];
export default function BugTracker(){return <CareerOSShell><PageHeader eyebrow="Project Control" title="Bug tracker" description="Known defects and verification state. This is deliberately separate from product roadmap so regressions stay visible." action={<Link href="/project-tracker" className="rounded-lg border bg-card px-4 py-2.5 text-sm font-semibold">Project tracker</Link>}/><div className="space-y-3">{bugs.map(([id,title,area,status,note])=><Card key={id}><div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between"><div><div className="flex flex-wrap items-center gap-2"><span className="font-mono text-xs text-primary">{id}</span><Badge tone={status==='fixed'?'good':status==='in review'?'warn':'blue'}>{status}</Badge><span className="text-xs text-muted-foreground">{area}</span></div><h2 className="mt-2 text-base font-semibold">{title}</h2><p className="mt-1 text-sm text-muted-foreground">{note}</p></div></div></Card>)}</div></CareerOSShell>}
