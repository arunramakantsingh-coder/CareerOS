'use client';

import { useEffect, useState } from 'react';
import { CareerOSShell, PageHeader, Card, Badge } from '@/components/CareerOSShell';
import DocumentUpload from '@/components/documents/DocumentUpload';
import { apiClient } from '@/lib/api/client';

const labels: Record<string, string> = { cv: 'CV / Resume', employment: 'Employment', certification: 'Certification', education: 'Education', project: 'Project', achievement: 'Achievement', other: 'Other' };

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>();
  const [profile, setProfile] = useState<any>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const [docs, stats, extracted] = await Promise.all([apiClient.documents(), apiClient.extractionSummary(), apiClient.extractedProfile()]);
      setDocuments(docs); setSummary(stats); setProfile(extracted);
    } catch (e: any) { setError(e.message || 'Unable to load the Career Vault'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return <CareerOSShell>
    <PageHeader eyebrow="Professional Evidence" title="Career Vault" description="Your professional documents are evidence. CareerOS preserves them, understands them, and uses verified information to build your career identity." action={<a href="/profile" className="rounded-xl border bg-card px-4 py-2.5 text-sm font-semibold hover:bg-muted">View profile →</a>} />

    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {[
        ['Documents', summary?.total_documents ?? documents.length, 'Evidence stored'],
        ['Processed', summary?.processed_documents ?? 0, 'Ready for intelligence'],
        ['Pending', summary?.pending_documents ?? 0, 'Awaiting extraction'],
        ['Profile signal', profile?.full_name ? 'Found' : 'Waiting', 'Latest extracted identity'],
      ].map(([label, value, copy]) => <Card key={label as string}><p className="text-xs font-medium text-muted-foreground">{label}</p><p className="mt-2 text-2xl font-bold">{value}</p><p className="mt-1 text-xs text-muted-foreground">{copy}</p></Card>)}
    </div>

    <div className="mt-5 grid gap-5 lg:grid-cols-[1.35fr_.65fr]">
      <Card title="Add professional evidence"><DocumentUpload onComplete={load} /></Card>
      <Card title="What CareerOS can discover"><div className="space-y-3">{['Identity & contact signals', 'Professional experience', 'Education & qualifications', 'Certifications & credentials', 'Skills & technologies', 'Projects & achievements'].map((item) => <div key={item} className="flex items-center gap-3 rounded-xl bg-muted/50 px-3 py-3"><span className="text-primary">✦</span><span className="text-sm font-medium">{item}</span></div>)}<p className="pt-2 text-xs leading-5 text-muted-foreground">Extracted values remain derived information. The original document remains the evidence source.</p></div></Card>
    </div>

    {profile && (profile.full_name || profile.skills?.length || profile.experiences?.length) && <Card title="CareerOS discovered new profile signals" className="mt-5"><div className="grid gap-4 md:grid-cols-3"><div><p className="text-xs text-muted-foreground">Identity</p><p className="mt-1 font-semibold">{profile.full_name || '—'}</p><p className="text-xs text-muted-foreground">{profile.title || profile.location || ''}</p></div><div><p className="text-xs text-muted-foreground">Skills discovered</p><p className="mt-1 text-xl font-bold">{profile.skills?.length || 0}</p></div><div><p className="text-xs text-muted-foreground">Experience signals</p><p className="mt-1 text-xl font-bold">{profile.experiences?.length || 0}</p></div></div><a href="/profile" className="mt-4 inline-flex rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground">Review my profile →</a></Card>}

    <Card title="Evidence inventory" className="mt-5">
      {error && <p className="mb-4 rounded-xl bg-red-500/5 p-3 text-sm text-red-600">{error}</p>}
      {loading ? <p className="text-sm text-muted-foreground">Loading your evidence…</p> : documents.length === 0 ? <div className="py-8 text-center"><p className="font-semibold">Your professional story starts here.</p><p className="mt-1 text-sm text-muted-foreground">Upload your CV, certificates, experience letters and other career evidence above.</p></div> : <div className="divide-y">{documents.map((doc) => <div key={doc.id} className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center"><div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary/10 text-xs font-bold text-primary">{(doc.file_type || 'DOC').toUpperCase().slice(0, 4)}</div><div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">{doc.original_filename || doc.filename}</p><p className="mt-1 text-xs text-muted-foreground">{labels[doc.document_category] || doc.document_category || 'Unclassified'} · {doc.file_size ? `${Math.max(1, Math.round(doc.file_size / 1024))} KB` : 'size unavailable'}</p></div><div className="flex items-center gap-2"><Badge tone={doc.extraction_status === 'complete' ? 'good' : doc.extraction_status === 'failed' ? 'warn' : 'blue'}>{doc.extraction_status || doc.status}</Badge><span className="text-[11px] text-muted-foreground">{doc.status}</span></div></div>)}</div>}
    </Card>
  </CareerOSShell>;
}
