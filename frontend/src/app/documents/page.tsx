'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import DocumentUpload from '@/components/documents/DocumentUpload';
import { apiClient } from '@/lib/api/client';
import { CareerOSShell, Card, PageHeader, Badge } from '@/components/CareerOSShell';

type DocumentRecord={id:string;filename?:string;file_size?:unknown;document_category?:unknown;document_subcategory?:unknown;status?:unknown;extraction_status?:unknown;classification_confidence?:unknown;created_at?:string;detected_type?:string;verification_status?:string;user_label?:string};
const text=(value:unknown,fallback='—')=>{if(value===null||value===undefined||value==='')return fallback;if(typeof value==='string'||typeof value==='number')return String(value);try{return JSON.stringify(value)}catch{return fallback}};

export default function DocumentsPage(){
 const {token,isAuthenticated,isLoading}=useAuth();const router=useRouter();const [documents,setDocuments]=useState<DocumentRecord[]>([]);const [loading,setLoading]=useState(true);const [reconcilingId,setReconcilingId]=useState<string|null>(null);
 useEffect(()=>{if(!isLoading&&!isAuthenticated)router.replace('/login')},[isLoading,isAuthenticated,router]);
 const load=async()=>{setLoading(true);try{const data=await apiClient.get<DocumentRecord[]>('/api/v1/documents/');setDocuments(Array.isArray(data)?data.filter(d=>text(d.document_category,'')==='cv'):[])}finally{setLoading(false)}};
 const reconcile=async(documentId:string)=>{setReconcilingId(documentId);try{await apiClient.post<any>(`/api/v1/identity/documents/${documentId}/ai-reconcile`,{});await load()}finally{setReconcilingId(null)}};
 useEffect(()=>{if(isAuthenticated&&token)void load()},[isAuthenticated,token]);
 if(isLoading||loading)return <div className="grid min-h-screen place-items-center bg-background">Loading CV workspace…</div>;if(!isAuthenticated)return null;
 return <CareerOSShell><PageHeader eyebrow="Professional Identity" title="CV & Documents" description="Upload CV versions here. Reconcile a completed CV with AI to build the Professional Profile." action={<Link href="/evidence-library" className="rounded-xl border bg-card px-4 py-2.5 text-sm font-semibold hover:bg-muted">Add Evidence</Link>}/>
 <section id="cv" className="scroll-mt-36"><Card title="Upload CV" className="techno-glow"><div className="grid gap-5 lg:grid-cols-[minmax(0,1.3fr)_minmax(260px,.7fr)]"><DocumentUpload category="cv" onUploadComplete={()=>void load()}/><div className="rounded-xl border bg-background/30 p-5"><p className="text-xs font-semibold uppercase tracking-[.14em] text-primary">CV-first identity building</p><h3 className="mt-2 text-lg font-semibold">One Professional Profile</h3><p className="mt-2 text-sm leading-6 text-muted-foreground">Upload multiple CV versions when useful. Reconciliation combines explicit CV facts into one CareerOS Professional Profile. Professional certificates and letters belong in the Evidence Library.</p><div className="mt-4 space-y-2 text-sm"><div className="flex justify-between"><span className="text-muted-foreground">CV versions</span><strong>{documents.length}</strong></div><div className="flex justify-between"><span className="text-muted-foreground">Processed</span><strong>{documents.filter(d=>text(d.extraction_status,'')==='complete').length}</strong></div></div></div></div></Card></section>
 <div className="mt-5"><Card title="CV versions"><div className="divide-y">{documents.length?documents.slice(0,20).map(doc=><div key={doc.id} className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between"><div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">{doc.user_label||doc.filename||'CV version'}</p><div className="mt-1 flex flex-wrap gap-2 text-xs"><Badge tone="blue">CV / Resume</Badge><Badge tone={text(doc.status,'')==='failed'?'warn':'muted'}>{text(doc.status,'unknown')}</Badge><Badge tone={text(doc.extraction_status,'')==='complete'?'good':'blue'}>{text(doc.extraction_status,'unknown')}</Badge>{typeof doc.classification_confidence==='number'&&<span>{Math.round(Number(doc.classification_confidence)*100)}% classified</span>}</div></div><div className="shrink-0"><button type="button" onClick={()=>void reconcile(doc.id)} disabled={reconcilingId!==null||text(doc.extraction_status,'')!=='complete'} className="rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50">{reconcilingId===doc.id?'Reconciling with AI…':'Reconcile with AI'}</button></div></div>):<div className="rounded-xl border border-dashed p-10 text-center"><p className="font-semibold">No CV uploaded</p><p className="mt-1 text-sm text-muted-foreground">Upload your CV to create the first Professional Profile draft.</p></div>}</div></Card></div>
 </CareerOSShell>;
}
