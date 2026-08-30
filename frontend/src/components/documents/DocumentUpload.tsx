'use client';

import { useRef, useState } from 'react';
import { apiClient } from '@/lib/api/client';

const ACCEPT = '.pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.tif,.tiff,.zip,.xls,.xlsx';

type Props = { onComplete?: (result: any) => void };

export default function DocumentUpload({ onComplete }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const folderRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const addFiles = (incoming: FileList | File[]) => {
    const next = Array.from(incoming).filter((file) => !files.some((existing) => existing.name === file.name && existing.size === file.size));
    setFiles((current) => [...current, ...next]);
    setError('');
  };

  const process = async () => {
    if (!files.length) return;
    setBusy(true); setError(''); setMessage('Preparing your professional evidence…'); setProgress(5);
    try {
      const result = await apiClient.uploadBulk(files, { onProgress: (index) => setProgress(Math.round(((index + 1) / files.length) * 90)) });
      setProgress(100);
      setMessage(`${result.created ?? result.documents?.length ?? files.length} document(s) added to your Career Vault.`);
      setFiles([]);
      onComplete?.(result);
    } catch (e: any) {
      setError(e.message || 'Upload failed');
      setMessage('');
    } finally { setBusy(false); }
  };

  return <div className="space-y-4">
    <div onDragEnter={(e) => { e.preventDefault(); setDragging(true); }} onDragOver={(e) => e.preventDefault()} onDragLeave={() => setDragging(false)} onDrop={(e) => { e.preventDefault(); setDragging(false); addFiles(e.dataTransfer.files); }} className={`rounded-3xl border-2 border-dashed p-7 text-center transition sm:p-10 ${dragging ? 'border-primary bg-primary/5' : 'border-border bg-muted/20 hover:border-primary/40'}`}>
      <div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-primary/10 text-2xl text-primary">◇</div>
      <h3 className="mt-4 text-lg font-semibold">Bring your professional life into CareerOS</h3>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-muted-foreground">Drop multiple files, a complete folder, or a ZIP archive. CareerOS will preserve the originals and prepare them for evidence-based profile enrichment.</p>
      <div className="mt-5 flex flex-wrap justify-center gap-2">
        <button onClick={() => inputRef.current?.click()} className="rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground">Choose files</button>
        <button onClick={() => folderRef.current?.click()} className="rounded-xl border bg-background px-4 py-2.5 text-sm font-semibold hover:bg-muted">Choose folder</button>
      </div>
      <p className="mt-3 text-[11px] text-muted-foreground">PDF · Word · images · spreadsheets · ZIP · scanned documents</p>
      <input ref={inputRef} type="file" multiple accept={ACCEPT} className="hidden" onChange={(e) => e.target.files && addFiles(e.target.files)} />
      <input ref={folderRef} type="file" multiple className="hidden" onChange={(e) => e.target.files && addFiles(e.target.files)} {...({ webkitdirectory: '', directory: '' } as any)} />
    </div>

    {files.length > 0 && <div className="rounded-2xl border bg-card p-4">
      <div className="flex items-center justify-between gap-3"><div><p className="text-sm font-semibold">Upload queue</p><p className="text-xs text-muted-foreground">{files.length} item{files.length === 1 ? '' : 's'} ready</p></div><button disabled={busy} onClick={process} className="rounded-xl bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground disabled:opacity-50">{busy ? 'Processing…' : 'Process all'}</button></div>
      <div className="mt-3 max-h-44 space-y-2 overflow-y-auto">{files.map((file, index) => <div key={`${file.name}-${index}`} className="flex items-center gap-3 rounded-xl bg-muted/50 px-3 py-2"><span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-background text-xs">{file.name.toLowerCase().endsWith('.zip') ? 'ZIP' : 'DOC'}</span><span className="min-w-0 flex-1"><span className="block truncate text-xs font-medium">{file.webkitRelativePath || file.name}</span><span className="text-[11px] text-muted-foreground">{Math.max(1, Math.round(file.size / 1024))} KB</span></span><button onClick={() => setFiles((current) => current.filter((_, i) => i !== index))} className="text-xs text-muted-foreground hover:text-foreground">Remove</button></div>)}</div>
      {busy && <div className="mt-4"><div className="h-2 overflow-hidden rounded-full bg-muted"><div className="h-full rounded-full bg-primary transition-all" style={{ width: `${progress}%` }} /></div><p className="mt-2 text-xs text-muted-foreground">{progress}% · {message || 'Processing evidence…'}</p></div>}
    </div>}

    {message && !busy && <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-sm text-emerald-700 dark:text-emerald-300">✓ {message}</div>}
    {error && <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-700 dark:text-red-300">{error}</div>}
  </div>;
}
