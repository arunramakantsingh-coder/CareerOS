"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient, resolveApiBaseUrl } from "@/lib/api/client";

interface Intelligence { profile: any; completeness: any; experience: any[]; skills: any[]; certifications: any[]; education: any[]; documents: any[]; connections: any[]; provenance: any[]; readiness: any; }

export default function ProfileIntelligencePage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<Intelligence | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const load = async () => {
    try { setData(await apiClient.get<Intelligence>("/api/v1/profile/intelligence")); }
    catch (e: any) { setMessage(e.message || "Failed to load profile intelligence"); }
    finally { setLoading(false); }
  };

  useEffect(() => { if (!isLoading && !isAuthenticated) router.push("/login"); }, [isLoading, isAuthenticated, router]);
  useEffect(() => { if (isAuthenticated) load(); }, [isAuthenticated]);

  const connectGmail = async () => {
    setMessage("");
    try {
      const token = localStorage.getItem("access_token") || localStorage.getItem("careeros_token");
      const response = await fetch(`${resolveApiBaseUrl()}/api/v1/auth/oauth/google/gmail/authorize-url`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "Unable to start Gmail authorization");
      window.location.href = body.authorization_url;
    } catch (e: any) { setMessage(e.message || "Unable to connect Gmail"); }
  };

  const syncLinkedIn = async () => {
    try { await apiClient.post("/api/v1/auth/oauth/linkedin/sync-profile", {}); setMessage("LinkedIn profile sync completed."); await load(); }
    catch (e: any) { setMessage(e.message || "LinkedIn sync failed"); }
  };

  if (isLoading || loading) return <div className="grid min-h-[60vh] place-items-center"><div className="rounded-xl border bg-card px-6 py-5 shadow-sm">Loading profile intelligence…</div></div>;
  if (!isAuthenticated || !data) return null;

  const score = Number(data.completeness?.overall_score || 0);
  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-4 border-b pb-6 sm:flex-row sm:items-end sm:justify-between">
        <div><p className="text-xs font-semibold uppercase tracking-[.14em] text-muted-foreground">Evidence-first profile</p><h1 className="mt-1 text-3xl font-bold tracking-tight">Career Intelligence Profile</h1><p className="mt-2 max-w-3xl text-sm text-muted-foreground">One canonical profile assembled from your documents, verified identity connections and user-confirmed information.</p></div>
        <div className="flex gap-2"><Link href="/documents" className="rounded-lg border px-4 py-2 text-sm font-semibold hover:bg-muted">Document Vault</Link><Link href="/profile" className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground">Edit Profile</Link></div>
      </header>

      {message && <div className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900 dark:bg-amber-950/30 dark:text-amber-200">{message}</div>}

      <section className="grid gap-4 md:grid-cols-4">
        <div className="rounded-xl border bg-card p-5"><p className="text-xs text-muted-foreground">Profile completeness</p><p className="mt-2 text-3xl font-bold">{score}%</p><div className="mt-3 h-2 rounded-full bg-muted"><div className="h-full rounded-full bg-primary" style={{ width: `${Math.min(score, 100)}%` }} /></div></div>
        <div className="rounded-xl border bg-card p-5"><p className="text-xs text-muted-foreground">Vault documents</p><p className="mt-2 text-3xl font-bold">{data.readiness.documents}</p><p className="mt-1 text-xs text-muted-foreground">{data.readiness.processed_documents} processed</p></div>
        <div className="rounded-xl border bg-card p-5"><p className="text-xs text-muted-foreground">Career evidence</p><p className="mt-2 text-3xl font-bold">{data.readiness.experiences + data.readiness.skills + data.readiness.certifications + data.readiness.education}</p><p className="mt-1 text-xs text-muted-foreground">experiences, skills, certs, education</p></div>
        <div className="rounded-xl border bg-card p-5"><p className="text-xs text-muted-foreground">Connections</p><p className="mt-2 text-3xl font-bold">{data.readiness.oauth_connections.length}</p><p className="mt-1 text-xs text-muted-foreground">Google / Gmail / LinkedIn</p></div>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-xl border bg-card p-5 lg:col-span-2"><h2 className="text-sm font-semibold">Canonical identity</h2><div className="mt-4 grid gap-4 sm:grid-cols-2">{[["Name",data.profile.full_name],["Title",data.profile.title],["Email",data.profile.primary_email],["Phone",data.profile.primary_phone],["Location",data.profile.location],["LinkedIn",data.profile.linkedin_url],["Years experience",data.profile.years_experience],["Reconciliation",data.profile.reconciliation_status]].map(([label,value])=><div key={label}><p className="text-xs text-muted-foreground">{label}</p><p className="mt-1 text-sm font-medium break-words">{value || "Not available"}</p></div>)}</div></div>
        <div className="rounded-xl border bg-card p-5"><h2 className="text-sm font-semibold">External connections</h2><div className="mt-4 space-y-3">{data.connections.map((c)=><div key={c.id} className="rounded-lg border p-3"><p className="font-medium capitalize">{c.provider}</p><p className="text-xs text-muted-foreground">{c.provider_email || "Connected"}</p><p className="mt-1 text-[11px] text-muted-foreground">Scopes: {(c.scopes || []).join(", ")}</p></div>)}{data.connections.length === 0 && <p className="text-sm text-muted-foreground">No external provider is connected yet.</p>}<div className="flex flex-wrap gap-2 pt-2"><button onClick={connectGmail} className="rounded-lg border px-3 py-2 text-xs font-semibold hover:bg-muted">Connect Gmail</button><button onClick={syncLinkedIn} className="rounded-lg border px-3 py-2 text-xs font-semibold hover:bg-muted">Sync LinkedIn</button></div></div></div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border bg-card p-5"><h2 className="text-sm font-semibold">Professional experience</h2><div className="mt-4 space-y-3">{data.experience.map((x)=><div key={x.id} className="rounded-lg border p-4"><div className="flex items-start justify-between gap-3"><div><p className="font-semibold">{x.title}</p><p className="text-sm text-muted-foreground">{x.company}{x.location ? ` • ${x.location}` : ""}</p></div><span className="rounded-full bg-primary/10 px-2 py-1 text-[11px] text-primary">{x.source_type || "profile"}</span></div>{x.achievements?.length > 0 && <p className="mt-2 text-xs text-muted-foreground">{x.achievements.slice(0,2).join(" • ")}</p>}</div>)}{!data.experience.length && <p className="text-sm text-muted-foreground">Upload a CV or employment evidence to build the timeline.</p>}</div></div>
        <div className="rounded-xl border bg-card p-5"><h2 className="text-sm font-semibold">Skills & certifications</h2><div className="mt-4 flex flex-wrap gap-2">{data.skills.map((x)=><span key={x.id} className="rounded-full bg-muted px-3 py-1.5 text-xs font-medium">{x.name}</span>)}{!data.skills.length && <p className="text-sm text-muted-foreground">No skills extracted yet.</p>}</div><div className="mt-5 space-y-2">{data.certifications.map((x)=><div key={x.id} className="rounded-lg border p-3"><p className="text-sm font-semibold">{x.name}</p><p className="text-xs text-muted-foreground">{x.issuer}{x.issue_date ? ` • ${String(x.issue_date).slice(0,10)}` : ""}</p></div>)}</div></div>
      </section>

      <section className="rounded-xl border bg-card p-5"><div className="flex items-center justify-between gap-3"><div><h2 className="text-sm font-semibold">Evidence provenance</h2><p className="mt-1 text-xs text-muted-foreground">Every extracted result remains linked to the document that produced it.</p></div><Link href="/documents" className="text-xs font-semibold text-primary">Open Vault →</Link></div><div className="mt-4 overflow-x-auto"><table className="w-full min-w-[680px] text-left text-sm"><thead><tr className="border-b text-xs text-muted-foreground"><th className="px-2 py-2">Document</th><th className="px-2 py-2">Extraction</th><th className="px-2 py-2">Status</th><th className="px-2 py-2">Confidence</th></tr></thead><tbody>{data.provenance.map((p)=><tr key={p.extraction_id} className="border-b last:border-0"><td className="px-2 py-3 font-medium">{p.document || p.document_id || "Unknown"}</td><td className="px-2 py-3 text-xs">{p.extraction_id.slice(0,8)}…</td><td className="px-2 py-3">{p.status}</td><td className="px-2 py-3 text-xs">{p.confidence?.overall != null ? `${Math.round(p.confidence.overall*100)}%` : "—"}</td></tr>)}</tbody></table>{!data.provenance.length && <p className="py-6 text-sm text-muted-foreground">No extraction evidence yet.</p>}</div></section>
    </div>
  );
}
