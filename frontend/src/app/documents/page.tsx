"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import DocumentBulkUpload from "@/components/documents/DocumentBulkUpload";
import { apiClient } from "@/lib/api/client";

interface DocumentRecord {
  id: string;
  original_filename: string;
  filename?: string;
  file_size: number;
  document_category: string;
  document_subcategory: string | null;
  status: string;
  extraction_status: string;
  classification_confidence?: number;
  created_at: string;
}

const categories = [
  ["all", "All documents"], ["cv", "CV / Resume"], ["employment", "Employment"],
  ["certification", "Certifications"], ["education", "Education"], ["project", "Projects"],
  ["achievement", "Achievements"], ["identity", "Identity"], ["other", "Other"],
];

export default function DocumentsPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [category, setCategory] = useState("all");

  useEffect(() => { if (!isLoading && !isAuthenticated) router.push("/login"); }, [isLoading, isAuthenticated, router]);
  useEffect(() => { if (isAuthenticated) fetchDocuments(); }, [isAuthenticated]);

  const fetchDocuments = async () => {
    try { setDocuments(await apiClient.get<DocumentRecord[]>("/api/v1/documents/")); setError(""); }
    catch (e: any) { setError(e.message || "Failed to fetch documents"); }
    finally { setLoading(false); }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Delete this evidence record? The original file will be removed from local Vault storage.")) return;
    try { await apiClient.delete(`/api/v1/documents/${id}`); setDocuments((items) => items.filter((x) => x.id !== id)); }
    catch (e: any) { setError(e.message || "Delete failed"); }
  };

  if (isLoading || loading) return <div className="grid min-h-[60vh] place-items-center"><div className="rounded-xl border bg-card px-6 py-5 shadow-sm">Loading Career Vault…</div></div>;
  if (!isAuthenticated) return null;

  const filtered = category === "all" ? documents : documents.filter((x) => x.document_category === category);
  const extracted = documents.filter((x) => x.extraction_status === "complete").length;
  const pending = documents.filter((x) => x.extraction_status === "pending").length;

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-4 border-b pb-6 sm:flex-row sm:items-end sm:justify-between">
        <div><p className="text-xs font-semibold uppercase tracking-[.14em] text-muted-foreground">Career evidence</p><h1 className="mt-1 text-3xl font-bold tracking-tight">Professional Document Vault</h1><p className="mt-2 max-w-3xl text-sm text-muted-foreground">Upload your professional life once. CareerOS preserves the original evidence, extracts structured facts and links those facts back to their source.</p></div>
        <div className="flex gap-2"><Link href="/profile/intelligence" className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground">Career Intelligence</Link><Link href="/profile" className="rounded-lg border px-4 py-2 text-sm font-semibold hover:bg-muted">Profile</Link></div>
      </header>

      {error && <div className="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-800 dark:bg-red-950/30 dark:text-red-200">{error}</div>}

      <section className="grid gap-4 md:grid-cols-4"><div className="rounded-xl border bg-card p-5"><p className="text-xs text-muted-foreground">Documents</p><p className="mt-1 text-3xl font-bold">{documents.length}</p></div><div className="rounded-xl border bg-card p-5"><p className="text-xs text-muted-foreground">Extracted</p><p className="mt-1 text-3xl font-bold">{extracted}</p></div><div className="rounded-xl border bg-card p-5"><p className="text-xs text-muted-foreground">Pending</p><p className="mt-1 text-3xl font-bold">{pending}</p></div><div className="rounded-xl border bg-card p-5"><p className="text-xs text-muted-foreground">Evidence categories</p><p className="mt-1 text-3xl font-bold">{new Set(documents.map((x) => x.document_category)).size}</p></div></section>

      <section className="rounded-xl border bg-card p-5"><DocumentBulkUpload onComplete={() => fetchDocuments()} /></section>

      <section className="rounded-xl border bg-card p-5">
        <div className="flex flex-col gap-3 border-b pb-4 sm:flex-row sm:items-center sm:justify-between"><div><h2 className="text-sm font-semibold">Vault inventory</h2><p className="mt-1 text-xs text-muted-foreground">Classification and extraction are derived from the document content; the original remains authoritative.</p></div><select value={category} onChange={(e) => setCategory(e.target.value)} className="rounded-lg border bg-background px-3 py-2 text-sm">{categories.map(([value,label]) => <option key={value} value={value}>{label}</option>)}</select></div>
        <div className="mt-4 divide-y">{filtered.map((doc) => <div key={doc.id} className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between"><div className="min-w-0"><p className="truncate font-medium">{doc.filename || doc.original_filename}</p><p className="truncate text-xs text-muted-foreground">Original: {doc.original_filename} • {(doc.file_size / 1024).toFixed(0)} KB</p><div className="mt-1 flex flex-wrap gap-2 text-[11px]"><span className="rounded-full bg-muted px-2 py-1">{doc.document_category || "other"}</span><span className="rounded-full bg-muted px-2 py-1">{doc.status}</span><span className="rounded-full bg-muted px-2 py-1">extraction: {doc.extraction_status}</span>{doc.classification_confidence != null && <span className="rounded-full bg-primary/10 px-2 py-1 text-primary">classification {Math.round(doc.classification_confidence * 100)}%</span>}</div></div><button onClick={() => handleDelete(doc.id)} className="self-start rounded-lg border px-3 py-2 text-xs font-semibold text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 sm:self-auto">Delete</button></div>)}{filtered.length === 0 && <div className="py-12 text-center text-sm text-muted-foreground">No documents in this category yet.</div>}</div>
      </section>
    </div>
  );
}
