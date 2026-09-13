'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { CareerOSShell, Card, PageHeader, Badge } from '@/components/CareerOSShell';
import DocumentBulkUpload from '@/components/documents/DocumentBulkUpload';
import { apiClient } from '@/lib/api/client';

export default function ProfessionalDocumentsPage(){
 const [documents,setDocuments]=useState<any[]>([]); const [loading,setLoading]=useState(true);
 const load=async()=>{try{const d=await apiClient.get<any[]>('/api/v1/documents/');setDocuments(Array.isArray(d)?d.filter(x=>x.document_category!=='cv'):[])}finally{setLoading(false)}};
 useEffect(()=>{void load()},[]);
 return <CareerOSShell><PageHeader eyebrow="Professional Identity" title="Professional Documents" description="Upload degrees, certificates, employment letters, awards and other professional records. CareerOS understands each document and links it to the right profile fact." action={<Link href="/evidence-library" className="rounded-xl border bg-card px-4 py-2.5 text-sm font-semibold hover:bg-muted">Open Evidence Library</Link>}/>
 <div className="grid gap-5 lg:grid-cols-[minmax(0,1.2fr)_minmax(280px,.8fr)]"><Card title="Upload professional evidence" className="techno-glow"><DocumentBulkUpload onComplete={()=>void load()}/></Card><Card title="How CareerOS handles it"><div className="space-y-3 text-sm leading-6 text-muted-foreground"><p><strong className="text-foreground">1. Understand</strong> — classify from document content, not the filename.</p><p><strong className="text-foreground">2. Extract</strong> — issuer, dates, credential numbers and relevant details.</p><p><strong className="text-foreground">3. Match</strong> — link only to profile facts that the document actually supports.</p><p><strong className="text-foreground">4. Evidence</strong> — dedicated documents strengthen completeness; uncertain matches remain reviewable.</p></div></Card></div>
 <div className="mt-5"><Card title="Professional evidence already uploaded">{loading?<p className="text-sm text-muted-foreground">Loading…</p>:documents.length?<div className="divide-y">{documents.slice(0,20).map((d:any)=><div key={d.id} className="flex items-center justify-between gap-3 py-3"><div className="min-w-0"><p className="truncate text-sm font-semibold">{d.user_label||d.filename||'Professional document'}</p><div className="mt-1 flex flex-wrap gap-2"><Badge tone="blue">{d.detected_type||`${d.document_category||'other'}:${d.document_subcategory||'unknown'}`}</Badge><Badge tone={d.verification_status==='verified'?'good':'muted'}>{d.verification_status||'reported'}</Badge></div></div><Link href="/evidence-library" className="shrink-0 rounded-lg border px-3 py-2 text-xs font-semibold">View evidence</Link></div>)}</div>:<div className="rounded-xl border border-dashed p-8 text-center"><p className="font-semibold">No supporting documents yet</p><p className="mt-1 text-sm text-muted-foreground">Upload the documents you have. Missing evidence will remain visible on the relevant Profile sections.</p></div>}</Card></div>
 </CareerOSShell>;
}
