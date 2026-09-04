"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/lib/api/client";
import { CareerOSShell, Badge, Card, PageHeader } from "@/components/CareerOSShell";

type DocumentRecord = {
  id: string;
  filename?: string;
  original_filename?: string;
  file_size?: number;
  document_category?: string;
  document_subcategory?: string;
  classification_confidence?: number;
  extraction_status?: string;
  status?: string;
  issuer?: string;
  source?: string;
  source_metadata?: Record<string, any>;
  created_at?: string;
};

const label = (value?: string) => (value || "Unclassified").replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

function detectedTitle(doc: DocumentRecord) {
  const meta = doc.source_metadata || {};
  const category = label(doc.document_category);
  const subtype = label(doc.document_subcategory);
  const issuer = doc.issuer || "";
  return [category, subtype !== "Unclassified" ? subtype : "", issuer].filter(Boolean).join(" · ");
}

export default function EvidenceLibraryPage() {
  const { token, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => { if (!isLoading && !isAuthenticated) router.replace("/login"); }, [isLoading, isAuthenticated, router]);
  useEffect(() => {
    if (!isAuthenticated || !token) return;
    (async () => {
      try {
        const result = await apiClient.get<DocumentRecord[]>("/api/v1/documents/");
        setDocuments(Array.isArray(result) ? result : []);
      } catch (e: any) { setError(e?.message || "Unable to load the evidence library."); }
      finally { setLoading(false); }
    })();
  }, [isAuthenticated, token]);

  const filtered = useMemo(() => documents.filter(doc => {
    const hay = `${doc.filename || ""} ${doc.original_filename || ""} ${doc.document_category || ""} ${doc.document_subcategory || ""} ${doc.issuer || ""}`.toLowerCase();
    return (filter === "all" || doc.document_category === filter) && hay.includes(query.toLowerCase());
  }), [documents, filter, query]);

  const stats = useMemo(() => ({
    total: documents.length,
    processed: documents.filter(x => x.extraction_status === "complete").length,
    verified: documents.filter(x => Number(x.classification_confidence || 0) >= .8).length,
    cv: documents.filter(x => x.document_category === "cv").length,
  }), [documents]);

  if (isLoading || loading) return <div className="grid min-h-screen place-items-center bg-background">Loading Evidence Library…</div>;
  if (!isAuthenticated) return null;

  return <CareerOSShell>
    <PageHeader eyebrow="Professional Identity · Evidence" title="Evidence Library" description="The evidence layer behind your CareerOS identity. Original files remain authoritative while classification, OCR, extracted text, provenance and profile links are derived intelligence." />
    {error && <div className="mb-5 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">{error}</div>}

    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {[["Evidence records", stats.total], ["Processed", stats.processed], ["High-confidence", stats.verified], ["CV versions", stats.cv]].map(([name, value]) => <Card key={String(name)}><p className="text-xs text-muted-foreground">{name}</p><p className="mt-1 text-3xl font-bold text-primary">{value}</p></Card>)}
    </div>

    <Card title="Evidence intelligence" className="mt-5 techno-glow">
      <div className="grid gap-3 md:grid-cols-3">
        {[["Authoritative source", "Original file is never replaced by derived OCR/PDF artifacts."], ["Content detection", "CareerOS identifies the document class and subtype from its content and filename."], ["Profile safety", "Only CV/resume sources automatically enrich the canonical profile; other evidence stays isolated until reviewed."]].map(([title, body]) => <div key={title} className="rounded-xl border bg-background/25 p-4"><p className="text-sm font-semibold">{title}</p><p className="mt-1 text-xs leading-5 text-muted-foreground">{body}</p></div>)}
      </div>
    </Card>

    <Card title="Evidence records" className="mt-5">
      <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search filename, detected type, issuer…" className="w-full rounded-xl border bg-background px-3.5 py-2.5 text-sm outline-none focus:border-primary lg:max-w-md" />
        <select value={filter} onChange={e => setFilter(e.target.value)} className="rounded-xl border bg-background px-3 py-2.5 text-sm"><option value="all">All evidence</option><option value="cv">CV / Resume</option><option value="employment">Employment</option><option value="certification">Certification</option><option value="education">Education</option><option value="project">Project</option><option value="achievement">Achievement</option><option value="other">Other</option></select>
      </div>
      {filtered.length === 0 ? <div className="rounded-xl border border-dashed p-12 text-center text-sm text-muted-foreground">No evidence matches this view.</div> : <div className="overflow-x-auto rounded-xl border"><table className="w-full min-w-[980px] text-left text-sm"><thead className="bg-background/60 text-xs uppercase tracking-wider text-muted-foreground"><tr><th className="px-4 py-3">Original file</th><th className="px-4 py-3">Detected document</th><th className="px-4 py-3">Evidence state</th><th className="px-4 py-3">Provenance</th><th className="px-4 py-3">Processing</th></tr></thead><tbody className="divide-y">{filtered.map(doc => { const meta = doc.source_metadata || {}; const confidence = Math.round(Number(doc.classification_confidence || 0) * 100); return <tr key={doc.id} className="align-top hover:bg-primary/5"><td className="px-4 py-4"><p className="max-w-[230px] truncate font-semibold" title={doc.original_filename}>{doc.original_filename || doc.filename || "Document"}</p><p className="mt-1 text-[11px] text-muted-foreground">{Math.round(Number(doc.file_size || 0) / 1024)} KB · {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : "date unavailable"}</p></td><td className="px-4 py-4"><p className="font-semibold text-primary">{detectedTitle(doc)}</p><p className="mt-1 text-xs text-muted-foreground">{confidence ? `${confidence}% classification confidence` : "Classification pending"}</p></td><td className="px-4 py-4"><div className="flex flex-wrap gap-2"><Badge tone={doc.status === "failed" ? "warn" : "good"}>{doc.status || "stored"}</Badge>{doc.document_subcategory && <Badge>{label(doc.document_subcategory)}</Badge>}</div><p className="mt-2 text-xs text-muted-foreground">Source: {doc.source || "upload"}</p></td><td className="px-4 py-4 text-xs text-muted-foreground"><p>SHA-256: <span className="font-mono">{meta.content_hash || "recorded"}</span></p><p className="mt-1">Relative path: {meta.relative_path || "root upload"}</p><p className="mt-1">Metadata sidecar: {meta.metadata_markdown_path ? "available" : "pending"}</p></td><td className="px-4 py-4 text-xs text-muted-foreground"><p>{doc.extraction_status || "pending"}</p><p className="mt-1">OCR: {meta.extraction?.ocr_required ? "used / attempted" : "not required"}</p><p className="mt-1">Derived PDF: {meta.derived_pdf_path ? "available" : "—"}</p></td></tr> })}</tbody></table></div>}
    </Card>
  </CareerOSShell>;
}
