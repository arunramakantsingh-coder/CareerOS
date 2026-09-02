"use client";

import { useRef, useState } from "react";
import { resolveApiBaseUrl } from "@/lib/api/client";
import { formatApiError } from "@/lib/api/errors";

interface DocumentUploadProps { onUploadComplete?: (document: any) => void; category?: string; subcategory?: string; }

export default function DocumentUpload({ onUploadComplete, category = "cv", subcategory }: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    setIsUploading(true); setError(null); setProgress(0);
    const allowed = [".pdf", ".doc", ".docx", ".txt", ".rtf"];
    const dot = file.name.lastIndexOf(".");
    const ext = dot >= 0 ? file.name.slice(dot).toLowerCase() : "";
    if (!allowed.includes(ext)) { setError("Please upload a PDF, DOC, DOCX, TXT or RTF CV."); setIsUploading(false); return; }
    if (file.size > 25 * 1024 * 1024) { setError("File size exceeds the 25MB limit."); setIsUploading(false); return; }
    const token = localStorage.getItem("access_token") || localStorage.getItem("careeros_token");
    if (!token) { setError("Please sign in to upload your CV."); setIsUploading(false); return; }

    const form = new FormData();
    form.append("files", file, file.name); form.append("relative_paths", file.name); form.append("document_category", category);
    if (subcategory) form.append("document_subcategory", subcategory);
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${resolveApiBaseUrl()}/api/v1/documents/batch-upload`);
    xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    xhr.upload.onprogress = e => { if (e.lengthComputable) setProgress(Math.round((e.loaded / e.total) * 100)); };
    xhr.onload = () => {
      try {
        const payload = JSON.parse(xhr.responseText || "{}");
        if (xhr.status >= 200 && xhr.status < 300) {
          const result = payload.results?.[0] || payload;
          setUploadedFile(result); setProgress(100); onUploadComplete?.(result);
        } else setError(formatApiError(payload, "Upload failed."));
      } catch { setError("The server returned an unexpected upload response."); }
      finally { setIsUploading(false); }
    };
    xhr.onerror = () => { setError("Network error. Check that CareerOS can reach the backend."); setIsUploading(false); };
    xhr.send(form);
  };

  return <div className="w-full">
    <div className={`relative rounded-2xl border-2 border-dashed p-8 text-center transition ${isDragging ? "border-primary bg-primary/5" : "border-border bg-background/25 hover:border-primary/50"}`}
      onDragEnter={e => { e.preventDefault(); setIsDragging(true); }} onDragLeave={e => { e.preventDefault(); setIsDragging(false); }} onDragOver={e => e.preventDefault()}
      onDrop={e => { e.preventDefault(); setIsDragging(false); if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]); }}>
      {isUploading ? <div className="space-y-4"><div className="mx-auto grid h-12 w-12 place-items-center rounded-full border border-primary/30 bg-primary/10 text-primary">↥</div><p className="text-sm font-semibold">Uploading and preparing your CV…</p><div className="mx-auto h-2 max-w-xl overflow-hidden rounded-full bg-muted"><div className="h-full bg-primary transition-all" style={{ width: `${progress}%` }} /></div><p className="text-xs text-muted-foreground">{progress}%</p></div>
      : uploadedFile ? <div className="space-y-3"><div className="text-4xl">✓</div><p className="font-semibold">{uploadedFile.filename || uploadedFile.original_filename || "CV"}</p><p className="text-sm text-muted-foreground">CV added to the evidence pipeline · {uploadedFile.extraction_status || uploadedFile.status || "uploaded"}</p><button onClick={() => { setUploadedFile(null); setProgress(0); if (fileInputRef.current) fileInputRef.current.value = ""; }} className="text-sm font-semibold text-primary">Upload another CV</button></div>
      : <div className="space-y-4"><div className="text-5xl">▤</div><div><h3 className="text-lg font-semibold">Upload your CV / Resume</h3><p className="mt-1 text-sm text-muted-foreground">Dedicated CV intake — kept separate from the Professional Document Vault.</p></div><button type="button" onClick={() => fileInputRef.current?.click()} className="rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground">Choose CV</button><p className="text-xs text-muted-foreground">PDF, DOC, DOCX, TXT, RTF · up to 25MB</p></div>}
    </div>
    <input ref={fileInputRef} type="file" accept=".pdf,.doc,.docx,.txt,.rtf" className="hidden" onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])} />
    {error && <div className="mt-3 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-500">{error}</div>}
  </div>;
}
