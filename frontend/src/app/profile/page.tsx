"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { CareerOSShell, Card, PageHeader, Badge, Button } from "@/components/CareerOSShell";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type FormState={full_name:string;title:string;location:string;primary_email:string;primary_phone:string;linkedin_url:string;summary:string};
const empty:FormState={full_name:"",title:"",location:"",primary_email:"",primary_phone:"",linkedin_url:"",summary:""};

export default function ProfilePage(){
  const {user,token,isAuthenticated,isLoading}=useAuth(); const router=useRouter();
  const [profile,setProfile]=useState<any>(null); const [completeness,setCompleteness]=useState<any>(null); const [form,setForm]=useState<FormState>(empty); const [editing,setEditing]=useState(false); const [loading,setLoading]=useState(true); const [message,setMessage]=useState("");
  useEffect(()=>{if(!isLoading&&!isAuthenticated)router.push('/login')},[isLoading,isAuthenticated,router]);
  const load=async()=>{if(!token)return; try{const [p,c]=await Promise.all([fetch(`${API_URL}/api/v1/profile/`,{headers:{Authorization:`Bearer ${token}`}}),fetch(`${API_URL}/api/v1/profile/completeness`,{headers:{Authorization:`Bearer ${token}`}})]); if(p.ok){const data=await p.json();setProfile(data);setForm({full_name:data.full_name||"",title:data.title||"",location:data.location||"",primary_email:data.primary_email||user?.email||"",primary_phone:data.primary_phone||"",linkedin_url:data.linkedin_url||"",summary:data.summary||""})} if(c.ok)setCompleteness(await c.json());}catch{setMessage('Unable to load your professional profile.')}finally{setLoading(false)}};
  useEffect(()=>{if(isAuthenticated&&token)load()},[isAuthenticated,token]);
  const save=async()=>{setMessage('');try{const r=await fetch(`${API_URL}/api/v1/profile/`,{method:'PUT',headers:{'Content-Type':'application/json',Authorization:`Bearer ${token}`},body:JSON.stringify(form)});if(!r.ok){const e=await r.json();throw new Error(e.detail||'Unable to save profile')}setProfile(await r.json());setEditing(false);setMessage('Profile updated.');await load();}catch(e:any){setMessage(e.message||'Unable to save profile')}};
  if(isLoading||loading)return <div className="grid min-h-screen place-items-center bg-background">Loading professional identity…</div>;
  if(!isAuthenticated)return null;
  const score=Number(completeness?.overall_score??profile?.completeness_score??0);
  const missing=completeness?.missing_items||[];

  return <CareerOSShell>
    <PageHeader eyebrow="Professional Identity" title="Your CareerOS profile" description="One canonical professional identity assembled from connected accounts, your CV, career documents, extracted evidence and information you confirm yourself." action={<div className="flex gap-2"><Badge tone={score>=80?'good':'blue'}>{score}% complete</Badge><Button onClick={()=>editing?save():setEditing(true)}>{editing?'Save profile':'Edit profile'}</Button></div>} />
    {message&&<div className="mb-4 rounded-xl border bg-card px-4 py-3 text-sm">{message}</div>}

    <div className="mb-5 grid gap-3 md:grid-cols-4">
      <Link href="/onboarding" className="rounded-xl border bg-card p-4 transition hover:border-primary/40"><p className="text-xs font-semibold text-primary">PROFILE SETUP</p><p className="mt-1 text-sm font-semibold">Onboarding & checklist</p><p className="mt-1 text-xs text-muted-foreground">Return anytime</p></Link>
      <Link href="/documents#cv" className="rounded-xl border bg-card p-4 transition hover:border-primary/40"><p className="text-xs font-semibold text-primary">CV / RESUME</p><p className="mt-1 text-sm font-semibold">Dedicated CV intake</p><p className="mt-1 text-xs text-muted-foreground">Upload and extract</p></Link>
      <Link href="/documents#vault" className="rounded-xl border bg-card p-4 transition hover:border-primary/40"><p className="text-xs font-semibold text-primary">DOCUMENT VAULT</p><p className="mt-1 text-sm font-semibold">Professional evidence</p><p className="mt-1 text-xs text-muted-foreground">Files · folders · ZIP</p></Link>
      <Link href="/profile/intelligence" className="rounded-xl border bg-card p-4 transition hover:border-primary/40"><p className="text-xs font-semibold text-primary">INTELLIGENCE</p><p className="mt-1 text-sm font-semibold">Evidence reconciliation</p><p className="mt-1 text-xs text-muted-foreground">Extraction & provenance</p></Link>
    </div>

    <div className="grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(300px,.55fr)]">
      <Card title="Canonical professional identity" className="techno-glow">
        <div className="grid gap-4 md:grid-cols-2">
          {[
            ['full_name','Full name','text'],['title','Professional title','text'],['location','Location','text'],['primary_email','Primary email','email'],['primary_phone','Primary phone','tel'],['linkedin_url','Primary LinkedIn','url']
          ].map(([key,label,type])=><label key={key} className="block"><span className="text-xs font-medium text-muted-foreground">{label}</span><input type={type} disabled={!editing} value={(form as any)[key]} onChange={e=>setForm({...form,[key]:e.target.value})} className={`mt-1.5 w-full rounded-lg border px-3 py-2.5 text-sm outline-none focus:border-primary ${editing?'bg-background':'bg-muted/25 text-foreground'}`} placeholder="Not available yet" /></label>)}
        </div>
        <label className="mt-4 block"><span className="text-xs font-medium text-muted-foreground">Professional summary</span><textarea rows={5} disabled={!editing} value={form.summary} onChange={e=>setForm({...form,summary:e.target.value})} className={`mt-1.5 w-full rounded-lg border px-3 py-2.5 text-sm outline-none focus:border-primary ${editing?'bg-background':'bg-muted/25'}`} placeholder="CareerOS will enrich this from evidence; you remain in control." /></label>
        {editing&&<div className="mt-4 flex gap-2"><Button onClick={save}>Save changes</Button><button onClick={()=>{setEditing(false);if(profile)setForm({full_name:profile.full_name||"",title:profile.title||"",location:profile.location||"",primary_email:profile.primary_email||user?.email||"",primary_phone:profile.primary_phone||"",linkedin_url:profile.linkedin_url||"",summary:profile.summary||""})}} className="rounded-lg border px-4 py-2.5 text-sm font-semibold hover:bg-muted">Cancel</button></div>}
      </Card>

      <div className="space-y-5">
        <Card title="Profile readiness"><div className="flex items-end justify-between"><div><p className="text-4xl font-bold">{score}%</p><p className="mt-1 text-xs text-muted-foreground">canonical profile completeness</p></div><Badge tone={score>=80?'good':'warn'}>{score>=80?'Ready to review':'Needs evidence'}</Badge></div><div className="mt-4 h-2.5 overflow-hidden rounded-full bg-muted"><div className="h-full rounded-full bg-primary" style={{width:`${Math.min(100,score)}%`}} /></div>{missing.length>0&&<div className="mt-4"><p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Missing / review</p><div className="mt-2 flex flex-wrap gap-2">{missing.slice(0,8).map((x:string)=><span key={x} className="rounded-full bg-muted px-2.5 py-1 text-xs">{x}</span>)}</div></div>}</Card>
        <Card title="Source hierarchy"><div className="space-y-3 text-sm">{[['Connected identity','Google / LinkedIn'],['Primary evidence','CV / Resume'],['Supporting evidence','Professional Document Vault'],['Reconciliation','Profile Intelligence'],['Final authority','You']].map(([a,b])=><div key={a} className="flex items-center justify-between gap-4 border-b pb-2 last:border-0"><span>{a}</span><span className="text-xs text-muted-foreground">{b}</span></div>)}</div></Card>
      </div>
    </div>
  </CareerOSShell>;
}
