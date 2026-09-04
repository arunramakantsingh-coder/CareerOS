'use client';
import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { CareerOSShell, Card, PageHeader, Button, Badge } from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';

function ApplicationStudioContent() {
  const params = useSearchParams();
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [apps, setApps] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>();
  const [pkg, setPkg] = useState<any>();
  const [truth, setTruth] = useState<any>();
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');
  const load = () => apiClient.applications().then(x => { setApps(x); const id = params.get('application'); if (id) setSelected(x.find((a:any) => a.id === id)); }).catch(e => setMsg(e.message));
  useEffect(() => { load(); }, [params]);
  const create = async () => { if (!title.trim()) { setMsg('Advertised title is required.'); return; } setBusy(true); try { const a = await apiClient.createApplication({ advertised_title: title, company, status: 'DISCOVERED' }); setSelected(a); setTitle(''); setCompany(''); await load(); } catch(e:any) { setMsg(e.message); } finally { setBusy(false); } };
  const generate = async () => { if (!selected) return; setBusy(true); try { setPkg(await apiClient.applicationPackage(selected.id)); await load(); } catch(e:any) { setMsg(e.message); } finally { setBusy(false); } };
  const check = async () => { if (!selected) return; try { setTruth(await apiClient.truthCheck(selected.id)); } catch(e:any) { setMsg(e.message); } };
  return <CareerOSShell><PageHeader eyebrow="Application Factory" title="Application Studio" description="Create an application record, generate a package from verified evidence, then run the truth gate before submission."/><Card title="Create application"><div className="grid gap-3 md:grid-cols-2"><input value={title} onChange={e=>setTitle(e.target.value)} placeholder="Employer advertised title" className="rounded-lg border px-3 py-2.5"/><input value={company} onChange={e=>setCompany(e.target.value)} placeholder="Company" className="rounded-lg border px-3 py-2.5"/></div><Button className="mt-3" disabled={busy} onClick={create}>{busy?'Working…':'Create application'}</Button>{msg&&<p className="mt-3 text-sm text-red-600">{msg}</p>}</Card><div className="mt-6 grid gap-4 lg:grid-cols-2"><Card title="Your applications"><div className="space-y-2">{apps.map(a=><button key={a.id} onClick={()=>{setSelected(a);setPkg(a.package)}} className={`w-full rounded-lg border p-3 text-left hover:bg-muted ${selected?.id===a.id?'border-primary bg-primary/5':''}`}><div className="flex justify-between"><span className="font-medium text-sm">{a.advertised_title}</span><Badge tone="blue">{a.status}</Badge></div><span className="text-xs text-muted-foreground">{a.company||'—'}</span></button>)}{!apps.length&&<p className="text-sm text-muted-foreground">No applications.</p>}</div></Card><Card title="Evidence-backed package">{selected?<><p className="text-sm text-muted-foreground">{selected.advertised_title} · {selected.company||'Company not set'}</p><div className="mt-4 flex flex-wrap gap-2"><Button onClick={generate} disabled={busy}>Generate package</Button><Button onClick={check} disabled={!selected.package&&!pkg} className="bg-slate-800">Run Truth & Compliance</Button></div>{(pkg||selected.package)&&<pre className="mt-4 max-h-96 overflow-auto rounded-lg bg-muted p-4 text-xs">{JSON.stringify(pkg||selected.package,null,2)}</pre>}{truth&&<div className="mt-4 rounded-lg border p-4"><Badge tone={truth.status==='PASS'?'good':'warn'}>{truth.status}</Badge><p className="mt-2 text-sm">{truth.issues?.length?`${truth.issues.length} claim(s) need review.`:'No unsupported claims detected by the v0.1 gate.'}</p></div>}</>:<p className="text-sm text-muted-foreground">Select an application to generate its package.</p>}</Card></div></CareerOSShell>;
}

export default function ApplicationStudio() {
  return <Suspense fallback={<CareerOSShell><PageHeader eyebrow="Application Factory" title="Application Studio" description="Loading application workspace…" /></CareerOSShell>}><ApplicationStudioContent /></Suspense>;
}
