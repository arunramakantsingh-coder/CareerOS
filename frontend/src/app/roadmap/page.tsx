'use client';
import Link from 'next/link';
import { CareerOSShell, Card, PageHeader, Badge } from '@/components/CareerOSShell';
const roadmap=[
 ['01','Foundation stability','Authentication, shell, database, runtime','verified'],
 ['02','Profile foundation','Identity, canonical profile model and evidence reconciliation','complete'],
 ['03','Profile Builder','One-page job-portal-grade profile: personal, resume, employment, education, certifications, IT skills, career profile and performance','active'],
 ['04','CV + Professional Document Vault','Dedicated CV intake, bulk files/folders, ZIP, scanner, OCR, classification and provenance','active'],
 ['05','Profile Intelligence','Evidence → structured profile → human confirmation → explainable provenance','next'],
 ['06','Personas','Role-specific professional positioning from the canonical profile','next'],
 ['07','Global Job Discovery','Multi-source global search and job intelligence','next'],
 ['08','Email Intelligence','Gmail-backed recruiting/application signals with explicit authorization','planned'],
 ['09','Company / Recruiter Intelligence','Employer context and decision support','planned'],
 ['10','Matching + Skill Gap','Evidence-based role fit and gap analysis','planned'],
 ['11','Application Factory + CRM','Tailored applications, tracking and follow-up','planned'],
 ['12','Live Interview Assistant','Real-time, permission-aware transcript assistance','later'],
 ['13','Analytics / Learning / Mobility','Outcome learning, remote intelligence and global mobility','later'],
];
export default function Roadmap(){return <CareerOSShell><PageHeader eyebrow="Project Control" title="CareerOS roadmap" description="Profile is the current product gate. Global job discovery begins only after the profile and evidence foundation are verified." action={<Link href="/project-tracker" className="rounded-lg border bg-card px-4 py-2.5 text-sm font-semibold">Project tracker</Link>}/><div className="space-y-3">{roadmap.map(([n,name,detail,status])=><div key={n} className="grid gap-3 rounded-xl border bg-card p-4 md:grid-cols-[48px_1fr_auto] md:items-center"><span className="font-mono text-sm text-primary">{n}</span><div><p className="font-semibold">{name}</p><p className="mt-1 text-sm text-muted-foreground">{detail}</p></div><Badge tone={status==='verified'||status==='complete'?'good':status==='active'?'blue':'muted'}>{status}</Badge></div>)}</div><div className="mt-5"><Card title="Sequence rule"><p className="text-sm leading-6">Profile first → evidence/profile intelligence → personas → global job discovery → application intelligence → live interview assistance. A later module must not destabilize an earlier verified module.</p></Card></div></CareerOSShell>}
