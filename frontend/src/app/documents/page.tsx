"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import DocumentUpload from "@/components/documents/DocumentUpload";
import DocumentBulkUpload from "@/components/documents/DocumentBulkUpload";
import { apiClient } from "@/lib/api/client";
import { CareerOSShell, Card, PageHeader, Badge } from "@/components/CareerOSShell";

type DocumentRecord={id:string;original_filename:string;filename?:string;file_size:number;document_category:string;document_subcategory?:string|null;status:string;extraction_status:string;classification_confidence?:number;created_at:string};

export default function DocumentsPage(){
  const {token,isAuthenticated,isLoading}=useAuth(); const router=useRouter();
  const [documents,setDocuments]=useState<DocumentRecord[]>([]); const [loading,setLoading]=useState(true); const [error,setError]=useState(""); const [category,setCategory]=useState("all");
  useEffect(()=>{if(!isLoading&&!isAuthenticated)router.push('/login')},[isLoading,isAuthenticated,router]);
  const load=async()=>{try{setDocuments(await apiClient.get<DocumentRecord[]>("/api/v1/documents/"));setError("")}catch(e:any){setError(e.message||"Unable to load document vault")}finally{setLoading(false)}};
  useEffect(()=>{if(isAuthenticated&&token)load()},[isAuthenticated,token]);
  const remove=async(id:string)=>{if(!confirm('Delete this document from CareerOS?'))return;try{await apiClient.delete(`/api/v1/documents/${id}`);setDocuments(v=>v.filter(d=>d.id!==id))}catch{alert('Unable to delete document')}};
  const filtered=useMemo(()=>category==='all'?documents:documents.filter(d=>d.document_category===category),[documents,category]);
  const cvs=documents.filter(d=>d.document_category==='cv'); const processed=documents.filter(d=>d.extraction_status==='complete').length;
  if(isLoading||loading)return <div className="grid min-h-screen place-items-center bg-background">Loading CV & Document Vault…</div>;
  if(!isAuthenticated)return null;

  return <CareerOSShell>
    <PageHeader eyebrow="Profile · Evidence" title="CV & Professional Document Vault" description="Your CV is a dedicated profile source. The Professional Document Vault is the broader evidence repository for employment, education, certifications, projects and other career records." action={<Link href="/profile/intelligence" className="rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground">Open Profile Intelligence</Link>} />
    {error&&<div className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-500">{error}</div>}

    <section id="cv" className="scroll-mt-36"><Card title="CV / Resume · dedicated intake" className="techno-glow"><div className="grid gap-5 lg:grid-cols-[minmax(0,1.3fr)_minmax(260px,.7fr)]"><DocumentUpload category="cv" onUploadComplete={()=>load()}/><div className="rounded-xl border bg-background/30 p-5"><p className="text-xs font-semibold uppercase tracking-[.14em] text-primary">Primary career source</p><h3 className="mt-2 text-lg font-semibold">Keep your CV independent</h3><p className="mt-2 text-sm leading-6 text-muted-foreground">CareerOS can use the CV to seed your professional timeline, skills and credentials while preserving the original document as evidence.</p><div className="mt-4 space-y-2 text-sm"><div className="flex justify-between"><span className="text-muted-foreground">CV versions in vault</span><strong>{cvs.length}</strong></div><div className="flex justify-between"><span className="text-muted-foreground">Extraction</span><Badge tone="blue">Evidence pipeline</Badge></div></div></div></div></Card></section>

    <section id="vault" className="mt-5 scroll-mt-36"><Card title="Professional Document Vault · bulk evidence"><div className="mb-4 grid gap-3 md:grid-cols-4">{[['Multiple files','Drop or browse many'],['Folder','Preserve relative paths'],['ZIP archive','Safe extraction'],['Camera / scan','Mobile evidence intake']].map(([a,b])=><div key={a} className="rounded-lg border bg-background/25 p-3"><p className="text-sm font-semibold">{a}</p><p className="mt-1 text-xs text-muted-foreground">{b}</p></div>)}</div><DocumentBulkUpload onComplete={()=>load()}/></Card></section>

    <div className="mt-5 grid gap-4 md:grid-cols-4"><Card><p className="text-xs text-muted-foreground">Total evidence</p><p className="mt-1 text-3xl font-bold">{documents.length}</p></Card><Card><p className="text-xs text-muted-foreground">CV / Resume</p><p className="mt-1 text-3xl font-bold">{cvs.length}</p></Card><Card><p className="text-xs text-muted-foreground">Extracted</p><p className="mt-1 text-3xl font-bold">{processed}</p></Card><Card><p className="text-xs text-muted-foreground">Profile link</p><Link href="/profile" className="mt-2 inline-block text-sm font-semibold text-primary">Back to Profile →</Link></Card></div>

    <div className="mt-5"><Card title="Evidence library"><div className="mb-4 flex flex-wrap items-center justify-between gap-3"><p className="text-sm text-muted-foreground">Original evidence and processing status remain visible.</p><select value={category} onChange={e=>setCategory(e.target.value)} className="rounded-lg border bg-background px-3 py-2 text-sm"><option value="all">All documents</option><option value="cv">CV / Resume</option><option value="employment">Employment</option><option value="certification">Certifications</option><option value="education">Education</option><option value="project">Projects</option><option value="achievement">Achievements</option><option value="other">Other</option></select></div>{filtered.length===0?<div className="rounded-xl border border-dashed p-10 text-center"><p className="font-semibold">No evidence in this view yet</p><p className="mt-1 text-sm text-muted-foreground">Upload your CV or professional documents above.</p></div>:<div className="divide-y">{filtered.map(doc=><div key={doc.id} className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between"><div className="min-w-0"><p className="truncate text-sm font-semibold">{doc.filename||doc.original_filename}</p><div className="mt-1 flex flex-wrap gap-2 text-xs text-muted-foreground"><span>{doc.document_category||'document'}</span><span>•</span><span>{(Number(doc.file_size||0)/1024).toFixed(0)} KB</span><Badge tone={doc.status==='failed'?'warn':'muted'}>{doc.status}</Badge><Badge tone={doc.extraction_status==='complete'?'good':'blue'}>{doc.extraction_status}</Badge>{doc.classification_confidence!=null&&<span>{Math.round(doc.classification_confidence*100)}% classification</span>}</div></div><button onClick={()=>remove(doc.id)} className="self-start rounded-lg border px-3 py-2 text-xs font-semibold text-red-500 hover:bg-red-500/10 sm:self-auto">Delete</button></div>)}</div>}</Card></div>
  </CareerOSShell>;
}
