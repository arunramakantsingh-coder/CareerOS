'use client';
import Link from 'next/link';
import { CareerOSShell, Card, PageHeader, Badge } from '@/components/CareerOSShell';

const bugs=[
 ['BUG-001','Documents upload error renders validation object','Document intake','fixed','API error values are normalized before they reach React children; vault rendering also hardens structured values.'],
 ['BUG-002','CV intake and bulk vault were visually/semantically mixed','Documents','fixed','Dedicated CV intake remains separate from the Professional Document Vault; bulk vault retains multi-file, folder, ZIP and scan intake.'],
 ['BUG-003','Horizontal navigation duplicated sidebar modules','Shell','fixed','Vertical navigation is now domain-level; horizontal navigation is contextual to the selected domain.'],
 ['BUG-004','Camera capture unreliable on mobile/LAN HTTP','Documents','mitigated','Scanner detects secure-context support and provides a mobile camera/file fallback. HTTPS is required for direct browser camera APIs outside localhost.'],
 ['BUG-005','OAuth buttons did not reliably reach provider authorization','Authentication','configuration required','Login now uses direct provider navigation and runtime API resolution. Provider credentials and exact provider-side redirect URIs must be configured; the UI must not pretend otherwise.'],
 ['BUG-006','Profile builder was split into tabs and missing complete job-portal fields','Profile','fixed in this milestone','Profile is now a single scrollable builder with personal details, resume positioning, employment 1..N, education, certifications, IT/key skills, career profile, evidence-backed accomplishments and Profile Performance.'],
 ['BUG-007','Typing in profile fields accepted only one character at a time','Profile UI','fixed','Reusable form controls are defined outside the page render function so React does not remount the input on every keystroke.'],
 ['BUG-008','Date fields lacked consistent calendar controls and seniority used free text','Profile UI','fixed','Date fields use native calendar controls; seniority, work preference, skill category and proficiency use controlled dropdowns.'],
 ['BUG-009','Mobile API could resolve to laptop localhost incorrectly','API / mobile','fixed','Browser-side API resolution derives port 8000 from the current hostname when no explicit API override is configured.'],
];

export default function BugTracker(){return <CareerOSShell><PageHeader eyebrow="Project Control" title="Bug tracker" description="Known defects, fixes and external configuration dependencies. A fixed UI defect is not the same as a provider-side configuration dependency." action={<Link href="/project-tracker" className="rounded-lg border bg-card px-4 py-2.5 text-sm font-semibold">Project tracker</Link>}/><div className="space-y-3">{bugs.map(([id,title,area,status,note])=><Card key={id}><div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between"><div><div className="flex flex-wrap items-center gap-2"><span className="font-mono text-xs text-primary">{id}</span><Badge tone={status==='fixed'?'good':status==='configuration required'?'warn':'blue'}>{status}</Badge><span className="text-xs text-muted-foreground">{area}</span></div><h2 className="mt-2 text-base font-semibold">{title}</h2><p className="mt-1 text-sm text-muted-foreground">{note}</p></div></div></Card>)}</div></CareerOSShell>}
