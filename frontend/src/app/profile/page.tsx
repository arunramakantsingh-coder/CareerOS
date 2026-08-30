'use client';

import { useEffect, useState } from 'react';
import { CareerOSShell, PageHeader, Card, Badge } from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';

function Section({ title, count, children }: { title: string; count?: number; children: React.ReactNode }) {
  return <Card className="h-full"><div className="flex items-center justify-between"><h2 className="font-semibold">{title}</h2>{typeof count === 'number' && <Badge tone="blue">{count}</Badge>}</div><div className="mt-4">{children}</div></Card>;
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>(); const [complete, setComplete] = useState<any>(); const [experiences, setExperiences] = useState<any[]>([]); const [skills, setSkills] = useState<any[]>([]); const [certs, setCerts] = useState<any[]>([]); const [education, setEducation] = useState<any[]>([]); const [extracted, setExtracted] = useState<any>();
  const [editing, setEditing] = useState(false); const [form, setForm] = useState<any>({}); const [saving, setSaving] = useState(false); const [message, setMessage] = useState(''); const [error, setError] = useState('');

  const load = async () => {
    try {
      const results = await Promise.allSettled([apiClient.candidateProfile(), apiClient.profileCompleteness(), apiClient.experiences(), apiClient.skills(), apiClient.certifications(), apiClient.educations(), apiClient.extractedProfile()]);
      const get = (i: number, fallback: any) => results[i].status === 'fulfilled' ? results[i].value : fallback;
      const p = get(0, null); setProfile(p); setComplete(get(1, null)); setExperiences(get(2, [])); setSkills(get(3, [])); setCerts(get(4, [])); setEducation(get(5, [])); setExtracted(get(6, null));
      if (p) setForm({ full_name: p.full_name || '', location: p.location || '', title: p.title || '', summary: p.summary || '', primary_email: p.primary_email || '', primary_phone: p.primary_phone || '', linkedin_url: p.linkedin_url || '' });
    } catch (e: any) { setError(e.message || 'Unable to load profile'); }
  };
  useEffect(() => { load(); }, []);

  const save = async (e: React.FormEvent) => { e.preventDefault(); setSaving(true); setError(''); setMessage(''); try { await apiClient.updateCandidateProfile(form); setMessage('Profile saved.'); setEditing(false); await load(); } catch (e: any) { setError(e.message || 'Could not save profile'); } finally { setSaving(false); } };

  return <CareerOSShell>
    <PageHeader eyebrow="My Career" title="Professional Identity" description="One canonical career profile, enriched by your evidence and kept reviewable whenever information conflicts." action={<div className="flex gap-2"><a href="/documents" className="rounded-xl border bg-card px-4 py-2.5 text-sm font-semibold hover:bg-muted">Open Vault</a>{profile && <button onClick={() => setEditing((v) => !v)} className="rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground">{editing ? 'Close editor' : 'Edit identity'}</button>}</div>} />

    <div className="grid gap-5 lg:grid-cols-[1.35fr_.65fr]">
      <Card>
        <div className="flex flex-col gap-5 sm:flex-row sm:items-center"><div className="grid h-20 w-20 shrink-0 place-items-center rounded-3xl bg-primary/10 text-2xl font-bold text-primary">{(profile?.full_name || 'A').split(/\s+/).slice(0, 2).map((x: string) => x[0]).join('').toUpperCase()}</div><div className="min-w-0"><p className="text-2xl font-bold">{profile?.full_name || extracted?.full_name || 'Your professional identity'}</p><p className="mt-1 text-base text-primary">{profile?.title || extracted?.title || 'Add your professional title'}</p><p className="mt-2 text-sm text-muted-foreground">{profile?.location || extracted?.location || 'Location not yet established'}</p></div></div>
        <div className="mt-5 grid gap-3 sm:grid-cols-3"><div className="rounded-2xl bg-muted/50 p-4"><p className="text-xs text-muted-foreground">Experience</p><p className="mt-1 text-lg font-bold">{profile?.years_experience ?? '—'}{profile?.years_experience ? '+' : ''} yrs</p></div><div className="rounded-2xl bg-muted/50 p-4"><p className="text-xs text-muted-foreground">Evidence status</p><p className="mt-1 text-lg font-bold">{profile?.reconciliation_status || 'pending'}</p></div><div className="rounded-2xl bg-muted/50 p-4"><p className="text-xs text-muted-foreground">Completeness</p><p className="mt-1 text-lg font-bold">{complete?.overall_score ?? profile?.completeness_score ?? 0}%</p></div></div>
      </Card>
      <Card title="CareerOS intelligence"><p className="text-sm leading-6 text-muted-foreground">Your profile is the canonical destination for evidence-derived career information. Upload authoritative documents in the Vault and review what CareerOS discovers before it becomes part of your professional story.</p><div className="mt-4"><Badge tone="good">Evidence-first</Badge></div></Card>
    </div>

    {editing && <Card title="Identity editor" className="mt-5"><form onSubmit={save} className="grid gap-4 md:grid-cols-2">{[['full_name','Full name'],['title','Professional title'],['location','Location'],['primary_email','Email'],['primary_phone','Phone'],['linkedin_url','LinkedIn URL']].map(([key,label]) => <label key={key} className="text-sm font-medium">{label}<input value={form[key] || ''} onChange={(e) => setForm({ ...form, [key]: e.target.value })} className="mt-1 w-full rounded-xl border bg-background px-3 py-2.5 text-sm" /></label>)}<label className="md:col-span-2 text-sm font-medium">Professional summary<textarea value={form.summary || ''} onChange={(e) => setForm({ ...form, summary: e.target.value })} rows={5} className="mt-1 w-full rounded-xl border bg-background px-3 py-2.5 text-sm" /></label><div className="md:col-span-2 flex gap-2"><button disabled={saving} className="rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground">{saving ? 'Saving…' : 'Save identity'}</button></div></form></Card>}

    {message && <p className="mt-4 rounded-xl bg-emerald-500/5 p-3 text-sm text-emerald-700 dark:text-emerald-300">✓ {message}</p>}{error && <p className="mt-4 rounded-xl bg-red-500/5 p-3 text-sm text-red-600">{error}</p>}

    <div className="mt-5 grid gap-5 lg:grid-cols-2">
      <Section title="Professional Experience" count={experiences.length}>{experiences.length ? <div className="space-y-4">{experiences.slice(0, 6).map((item) => <div key={item.id} className="border-l-2 border-primary/20 pl-4"><p className="font-semibold">{item.title}</p><p className="text-sm text-primary">{item.company}</p><p className="mt-1 text-xs text-muted-foreground">{item.start_date ? new Date(item.start_date).getFullYear() : '—'} — {item.is_current ? 'Present' : item.end_date ? new Date(item.end_date).getFullYear() : '—'}</p></div>)}</div> : <p className="text-sm text-muted-foreground">No experience records yet. Upload an experience letter or CV to discover them.</p>}</Section>
      <Section title="Skills" count={skills.length}>{skills.length ? <div className="flex flex-wrap gap-2">{skills.slice(0, 30).map((skill) => <Badge key={skill.id} tone="blue">{skill.name}</Badge>)}</div> : <p className="text-sm text-muted-foreground">Skills will appear here when supported evidence is processed.</p>}</Section>
      <Section title="Certifications" count={certs.length}>{certs.length ? <div className="space-y-3">{certs.map((cert) => <div key={cert.id} className="rounded-xl bg-muted/50 p-3"><p className="font-semibold">{cert.name}</p><p className="text-xs text-muted-foreground">{cert.issuer}</p></div>)}</div> : <p className="text-sm text-muted-foreground">No certifications discovered yet.</p>}</Section>
      <Section title="Education" count={education.length}>{education.length ? <div className="space-y-3">{education.map((item) => <div key={item.id} className="rounded-xl bg-muted/50 p-3"><p className="font-semibold">{item.degree}</p><p className="text-xs text-muted-foreground">{item.institution}{item.field_of_study ? ` · ${item.field_of_study}` : ''}</p></div>)}</div> : <p className="text-sm text-muted-foreground">No education records discovered yet.</p>}</Section>
    </div>

    {complete && <Card title="Profile intelligence map" className="mt-5"><div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{Object.entries(complete.breakdown || {}).map(([key, value]) => <div key={key} className="rounded-2xl border bg-muted/20 p-4"><div className="flex justify-between gap-3"><span className="text-xs font-medium">{key}</span><span className="text-xs font-bold text-primary">{String(value)}%</span></div><div className="mt-3 h-1.5 rounded-full bg-muted"><div className="h-full rounded-full bg-primary" style={{ width: `${Number(value) || 0}%` }} /></div></div>)}</div>{complete.missing_items?.length > 0 && <p className="mt-4 text-xs text-muted-foreground">Next signals to review: {complete.missing_items.join(' · ')}</p>}</Card>}
  </CareerOSShell>;
}
