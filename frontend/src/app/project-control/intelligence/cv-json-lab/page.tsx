'use client';

import { useEffect, useMemo, useState } from 'react';
import { CareerOSShell, PageHeader, Card, Badge, Button } from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';

const DEFAULT_TEMPLATE = '{"profile":{"full_name":null,"title":null,"summary":null,"location":null,"email":null,"phone":null,"linkedin":null},"employment":[{"employer":"","title":"","client":null,"start_date":null,"end_date":null,"location":null,"description":null,"responsibilities":[],"achievements":[],"technologies":[]}],"education":[{"institution":"","degree":"","field_of_study":null,"start_date":null,"end_date":null,"grade":null}],"certifications":[{"name":"","issuer":null,"issue_date":null,"expiry_date":null,"credential_reference":null}],"skills":[],"projects":[{"name":"","description":null,"role":null,"technologies":[]}],"accomplishments":[{"title":"","description":null,"date":null}]}';

const DEFAULT_INSTRUCTION = 'Extract the uploaded CV into the exact JSON format supplied. The CV is the only source of truth. Never invent or infer facts. Preserve every genuine employment role separately; never merge separate roles at the same employer. Keep each section in its own JSON section. Return minified JSON only.';

type SourceDocument = {
  id: string;
  filename: string;
  stored_filename?: string;
  category: string;
  processing_stage?: string;
  extraction_status?: string;
  created_at?: string | null;
  chars: number;
  words: number;
  has_extracted_text: boolean;
};

function compactJson(value: unknown) {
  return JSON.stringify(value);
}

function topLevelSections(value: unknown): string[] {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return [];
  return Object.keys(value as Record<string, unknown>);
}

function collectPaths(value: unknown, prefix = ''): string[] {
  if (Array.isArray(value)) {
    const base = prefix || '[]';
    if (!value.length) return [base];
    return value.flatMap((item) => collectPaths(item, `${base}[]`));
  }
  if (value && typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>);
    if (!entries.length) return [prefix || '{}'];
    return entries.flatMap(([key, item]) => collectPaths(item, prefix ? `${prefix}.${key}` : key));
  }
  return [prefix || 'value'];
}

export default function CvJsonLab() {
  const [template, setTemplate] = useState(DEFAULT_TEMPLATE);
  const [instruction, setInstruction] = useState(DEFAULT_INSTRUCTION);
  const [sources, setSources] = useState<SourceDocument[]>([]);
  const [documentId, setDocumentId] = useState('');
  const [sourceText, setSourceText] = useState('');
  const [manualOverride, setManualOverride] = useState(false);
  const [output, setOutput] = useState('');
  const [busy, setBusy] = useState(false);
  const [loadingSource, setLoadingSource] = useState(false);
  const [message, setMessage] = useState('');
  const [provider, setProvider] = useState<string | null>(null);
  const [model, setModel] = useState<string | null>(null);
  const [traceId, setTraceId] = useState<string | null>(null);
  const [validation, setValidation] = useState<any>(null);
  const [mapping, setMapping] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [templateError, setTemplateError] = useState('');

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem('careeros.cv-json-lab');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (typeof parsed.template === 'string') setTemplate(parsed.template);
        if (typeof parsed.instruction === 'string') setInstruction(parsed.instruction);
        if (typeof parsed.documentId === 'string') setDocumentId(parsed.documentId);
      }
    } catch { /* ignore invalid local test state */ }
    void loadSource();
  }, []);

  const loadSource = async () => {
    setLoadingSource(true);
    try {
      const result = await apiClient.get<any>('/api/v1/developer/cv-json-lab/source');
      const docs = Array.isArray(result?.documents) ? result.documents : [];
      setSources(docs);
      const preferred = documentId && docs.some((doc: SourceDocument) => doc.id === documentId) ? documentId : result?.selected_document_id || docs[0]?.id || '';
      setDocumentId(preferred);
      const selected = docs.find((doc: SourceDocument) => doc.id === preferred);
      setSourceText(selected?.has_extracted_text ? `Detected uploaded CV: ${selected.filename}\n\nThe actual extracted CV text is held server-side and is sent directly from Document Vault when the test runs.` : '');
      setMessage(docs.length ? `Detected ${docs.length} uploaded CV${docs.length === 1 ? '' : 's'}. The latest CV is selected automatically.` : 'No uploaded CV is currently available in Document Vault.');
    } catch (error: any) {
      setMessage(error?.message || 'Unable to load uploaded CVs.');
    } finally {
      setLoadingSource(false);
    }
  };

  const selectedSource = sources.find((doc) => doc.id === documentId) || sources[0] || null;

  const analysis = useMemo(() => {
    try {
      const parsed = JSON.parse(template);
      const compact = compactJson(parsed);
      return {
        parsed,
        compact,
        valid: true,
        chars: template.length,
        compactChars: compact.length,
        sections: topLevelSections(parsed),
        paths: collectPaths(parsed),
      };
    } catch (error: any) {
      return { parsed: null, compact: '', valid: false, chars: template.length, compactChars: 0, sections: [], paths: [], error: error?.message || 'Invalid JSON' };
    }
  }, [template]);

  const instructionStats = useMemo(() => ({
    chars: instruction.length,
    words: instruction.trim() ? instruction.trim().split(/\s+/).length : 0,
  }), [instruction]);

  const saveLocally = () => {
    window.localStorage.setItem('careeros.cv-json-lab', JSON.stringify({ template, instruction, documentId }));
    setMessage('JSON contract, instruction and source selection saved locally in this browser.');
  };

  const resetDefaults = () => {
    setTemplate(DEFAULT_TEMPLATE);
    setInstruction(DEFAULT_INSTRUCTION);
    setMessage('Default production-shaped compact JSON contract restored.');
  };

  const runTest = async () => {
    setMessage('');
    setOutput('');
    setValidation(null);
    setMapping(null);
    setMetrics(null);
    setTemplateError('');

    if (!analysis.valid || !analysis.parsed || Array.isArray(analysis.parsed)) {
      setTemplateError(analysis.error || 'JSON contract must be a valid top-level JSON object.');
      return;
    }
    if (!documentId && !selectedSource) {
      setMessage('No uploaded CV is available in Document Vault. Upload the CV through the normal application first.');
      return;
    }

    setBusy(true);
    try {
      const result = await apiClient.post<any>('/api/v1/developer/cv-json-lab/extract', {
        document_id: documentId || null,
        instruction,
        template: analysis.parsed,
      });
      setOutput(String(result?.output || ''));
      setProvider(result?.provider || null);
      setModel(result?.model || null);
      setTraceId(result?.trace_id || null);
      setValidation(result?.validation || null);
      setMapping(result?.application_mapping || null);
      setMetrics(result?.metrics || null);
      setMessage('Extraction completed from the actual uploaded CV. The same canonical CareerOS mapping path was exercised inside a rollback savepoint; the real Professional Profile was not changed.');
    } catch (error: any) {
      setMessage(error?.message || 'CV JSON extraction failed.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <CareerOSShell>
      <PageHeader
        eyebrow="Project Control · Intelligence · Developer Lab"
        title="CV JSON Extraction Lab"
        description="Application-level replica of CV reconciliation: the lab detects the uploaded CV from Document Vault, sends the editable JSON contract and short instruction through the same Global Intelligence routing path, parses compact JSON, and exercises the normal CareerOS profile mapping without committing it."
        action={<Badge tone="blue">DRY RUN · NO PROFILE COMMIT</Badge>}
      />

      {message && <div className="mb-5 rounded-xl border bg-card px-4 py-3 text-sm">{message}</div>}

      <div className="grid gap-5 xl:grid-cols-2">
        <Card>
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">1 · Actual output contract</p>
              <h2 className="mt-2 text-lg font-bold">JSON format sent to AI</h2>
              <p className="mt-1 text-sm text-muted-foreground">This is the real JSON contract for this lab request. CareerOS compacts it before sending and also derives a structured-output schema from it.</p>
            </div>
            <Badge tone={analysis.valid ? 'good' : 'warn'}>{analysis.valid ? 'VALID JSON' : 'INVALID JSON'}</Badge>
          </div>
          <textarea value={template} onChange={(e) => setTemplate(e.target.value)} spellCheck={false} className="mt-4 min-h-[430px] w-full rounded-xl border bg-background p-4 font-mono text-xs leading-5 outline-none focus:ring-2 focus:ring-primary/30" />
          {templateError && <p className="mt-2 text-sm text-destructive">{templateError}</p>}
          <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
            <Stat label="Entered chars" value={analysis.chars.toLocaleString()} />
            <Stat label="Compact chars" value={analysis.compactChars.toLocaleString()} />
            <Stat label="Sections" value={String(analysis.sections.length)} />
            <Stat label="Fields / paths" value={String(analysis.paths.length)} />
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {analysis.sections.map((section) => <Badge key={section} tone="blue">{section}</Badge>)}
          </div>
        </Card>

        <Card>
          <p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">2 · Small AI instruction</p>
          <h2 className="mt-2 text-lg font-bold">Instruction actually sent</h2>
          <p className="mt-1 text-sm text-muted-foreground">Keep this short. The CV and JSON contract carry the data.</p>
          <textarea value={instruction} onChange={(e) => setInstruction(e.target.value)} spellCheck={false} className="mt-4 min-h-[210px] w-full rounded-xl border bg-background p-4 font-mono text-xs leading-5 outline-none focus:ring-2 focus:ring-primary/30" />
          <div className="mt-3 flex flex-wrap gap-2"><Badge tone="blue">{instructionStats.chars.toLocaleString()} chars</Badge><Badge tone="muted">{instructionStats.words.toLocaleString()} words</Badge></div>
          <div className="mt-5 flex flex-wrap gap-2">
            <Button onClick={saveLocally}>Save Test Contract</Button>
            <Button onClick={resetDefaults}>Restore Defaults</Button>
          </div>
        </Card>
      </div>

      <Card className="mt-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">3 · Actual Document Vault source</p>
            <h2 className="mt-2 text-lg font-bold">Uploaded CV detected by CareerOS</h2>
            <p className="mt-1 text-sm text-muted-foreground">No copy/paste is required. The backend reads the extracted text stored with the selected uploaded CV at execution time.</p>
          </div>
          <Button onClick={loadSource} disabled={loadingSource}>{loadingSource ? 'Detecting CV…' : 'Refresh Uploaded CVs'}</Button>
        </div>
        <div className="mt-4 grid gap-3 lg:grid-cols-[1fr_auto_auto_auto]">
          <select value={documentId} onChange={(e) => setDocumentId(e.target.value)} className="rounded-xl border bg-background px-4 py-3 text-sm">
            {!sources.length && <option value="">No uploaded CV found</option>}
            {sources.map((doc) => <option key={doc.id} value={doc.id}>{doc.filename} · {doc.chars.toLocaleString()} chars</option>)}
          </select>
          {selectedSource && <Badge tone="good">{selectedSource.chars.toLocaleString()} CV chars</Badge>}
          {selectedSource && <Badge tone="muted">{selectedSource.words.toLocaleString()} words</Badge>}
          {selectedSource && <Badge tone="blue">{selectedSource.processing_stage || 'vault'}</Badge>}
        </div>
        <div className="mt-4 rounded-xl border bg-muted/20 p-4">
          <p className="text-xs font-bold uppercase tracking-[.14em] text-muted-foreground">CV text path</p>
          <p className="mt-2 text-sm leading-6">Document Vault → extracted_text → compact request envelope → Global Intelligence → compact JSON → CareerOS parser/normalizer → canonical profile mapping (dry-run rollback).</p>
        </div>
        <label className="mt-4 flex items-center gap-2 text-sm">
          <input type="checkbox" checked={manualOverride} onChange={(e) => setManualOverride(e.target.checked)} />
          Enable debug CV text override
        </label>
        {manualOverride && <textarea value={sourceText} onChange={(e) => setSourceText(e.target.value)} spellCheck={false} className="mt-3 min-h-[220px] w-full rounded-xl border bg-background p-4 font-mono text-xs leading-5" placeholder="Debug-only override. The normal test path uses the actual uploaded CV from Document Vault." />}
        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-muted-foreground">The normal test never uses browser-pasted CV text. Debug override is isolated and does not modify Document Vault.</p>
          <Button onClick={runTest} disabled={busy || !analysis.valid || (!documentId && !selectedSource)}>{busy ? 'Running application-level extraction…' : 'Run CV Reconciliation Lab'}</Button>
        </div>
      </Card>

      <Card className="mt-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">4 · Only result</p>
            <h2 className="mt-2 text-lg font-bold">CV JSON outcome</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {provider && <Badge tone="good">{provider}</Badge>}
            {model && <Badge tone="blue">{model}</Badge>}
            {traceId && <Badge tone="muted">trace {traceId.slice(0, 8)}</Badge>}
            {validation && <Badge tone={validation.valid_json && !validation.missing_sections?.length ? 'good' : 'warn'}>{validation.valid_json ? 'VALID JSON' : 'INVALID JSON'}</Badge>}
          </div>
        </div>
        {validation?.missing_sections?.length ? <p className="mt-3 text-sm text-destructive">Missing contract sections: {validation.missing_sections.join(', ')}</p> : null}
        <textarea value={output} readOnly placeholder="The AI's compact CV JSON outcome will appear here..." className="mt-4 min-h-[500px] w-full rounded-xl border bg-background p-4 font-mono text-xs leading-5 outline-none" />
        {metrics && <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
          <Stat label="CV chars" value={String(metrics.cv_chars)} />
          <Stat label="Instruction" value={String(metrics.instruction_chars)} />
          <Stat label="JSON compact" value={String(metrics.compact_template_chars)} />
          <Stat label="Prompt" value={String(metrics.prompt_chars)} />
          <Stat label="Output" value={String(metrics.output_chars)} />
          <Stat label="Mapping rows" value={String(mapping?.would_apply?.experiences || 0)} />
        </div>}
        {mapping && <div className="mt-4 rounded-xl border bg-muted/20 p-4 text-sm">CareerOS canonical mapping check: <strong>profile mutation = false</strong>. The returned JSON was passed through the same normalization/persistence mapper inside a rollback savepoint.</div>}
      </Card>
    </CareerOSShell>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return <div className="rounded-xl border bg-muted/20 px-3 py-3"><p className="text-[10px] font-bold uppercase tracking-[.14em] text-muted-foreground">{label}</p><p className="mt-1 text-sm font-semibold">{value}</p></div>;
}
