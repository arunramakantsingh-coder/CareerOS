'use client';
import Link from 'next/link';
import { CareerOSShell, Card, PageHeader, Badge } from '@/components/CareerOSShell';
const roadmap=[
 ['01','Foundation stability','Authentication, shell, database, runtime','verified'],
 ['02','Profile foundation','Identity, profile model, evidence reconciliation','active'],
 ['03','CV + Professional Document Vault','Dedicated CV intake, bulk evidence, OCR, classification, provenance','active'],
 ['04','Profile intelligence','Evidence → structured profile → human confirmation','active'],
 ['05','Personas','Role-specific professional positioning','next'],
 ['06','Global Job Discovery','Multi-source global search and job intelligence','next'],
 ['07','Email Intelligence','Gmail-backed recruiting/application signals','planned'],
 ['08','Company / Recruiter Intelligence','Employer context and decision support','planned'],
 ['09','Matching + Skill Gap','Evidence-based role fit and gap analysis','planned'],
 ['10','Application Factory + CRM','Tailored applications, tracking and follow-up','planned'],
 ['11','Live Interview Assistant','Real-time, permission-aware transcript assistance','later'],
 ['12','Analytics / Learning / Mobility','Outcome learning, remote intelligence and global mobility','later'],
];
export default function Roadmap(){return <CareerOSShell><PageHeader eyebrow="Project Control" title="CareerOS roadmap" description="Product sequencing from the current profile foundation toward the complete global career operating system." action={<Link href="/project-tracker" className="rounded-lg border bg-card px-4 py-2.5 text-sm font-semibold">Project tracker</Link>}/><div className="space-y-3">{roadmap.map(([n,name,detail,status])=><div key={n} className="grid gap-3 rounded-xl border bg-card p-4 md:grid-cols-[48px_1fr_auto] md:items-center"><span className="font-mono text-sm text-primary">{n}</span><div><p className="font-semibold">{name}</p><p className="mt-1 text-sm text-muted-foreground">{detail}</p></div><Badge tone={status==='verified'?'good':status==='active'?'blue':'muted'}>{status}</Badge></div>)}</div><div className="mt-5 rounded-xl border bg-primary/5 p-5"><p className="text-xs font-semibold uppercase tracking-[.16em] text-primary">Sequence rule</p><p className="mt-2 text-sm leading-6">Profile first → global job discovery → application intelligence → live interview assistance. A later module must not destabilize an earlier verified module.</p></div></CareerOSShell>}
