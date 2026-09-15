'use client';

import { useEffect, useMemo, useState } from 'react';
import { CareerOSShell, PageHeader, Card, Badge, Button } from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';

const DEFAULT_TEMPLATE = '{"profile":{"full_name":null,"title":null,"summary":null,"location":null,"email":null,"phone":null,"linkedin":null},"employment":[{"employer":"","title":"","client":null,"start_date":null,"end_date":null,"location":null,"description":null,"responsibilities":[],"achievements":[],"technologies":[]}],"education":[{"institution":"","degree":"","field_of_study":null,"start_date":null,"end_date":null,"grade":null}],"certifications":[{"name":"","issuer":null,"issue_date":null,"expiry_date":null,"credential_reference":null}],"skills":[],"projects":[{"name":"","description":null,"role":null,"technologies":[]}],"accomplishments":[{"title":"","description":null,"date":null}]}';
const DEFAULT_INSTRUCTION = 'Extract the uploaded CV into the exact JSON format supplied. The CV is the only source of truth. Never invent or infer facts. Preserve every genuine employment role separately; never merge separate roles at the same employer. Keep each section in its own JSON section. Return minified JSON only.';

type SourceDocument = { id: string; filename: string; chars: number; words: number; processing_stage?: string; has_extracted_text: boolean };
type ModelOption = { name: string; source?: string; size?: number; parameter_size?: string; quantization_level?: string; family?: string };

function compact(value: unknown) { return JSON.stringify(value); }
function sections(value: unknown): string[] { return value && typeof value === 'object' && !Array.isArray(value) ? Object.keys(value as Record<string, unknown>) : []; }
function paths(value: unknown, prefix = ''): string[] {
  if (Array.isArray(value)) { const base = prefix || '[]'; return value.length ? value.flatMap((item) => paths(item, `${base}[]`)) : [base]; }
  if (value && typeof value === 'object') { const entries = Object.entries(value as Record<string, unknown>); return entries.length ? entries.flatMap(([key, item]) => paths(item, prefix ? `${prefix}.${key}` : key)) : [prefix || '{}']; }
  return [prefix || 'value'];
}
function fmtMs(value: unknown) { return value == null ? '—' : `${Number(value).toFixed(1)} ms`; }
function fmtDuration(value: unknown) { if (value == null) return '—'; const ms = Number(value); return ms >= 1000 ? `${(ms / 1000).toFixed(2)} s` : `${ms.toFixed(0)} ms`; }

export default function CvJsonLabClient() {
  const [template, setTemplate] = useState(DEFAULT_TEMPLATE);
  const [instruction, setInstruction] = useState(DEFAULT_INSTRUCTION);
  const [sources, setSources] = useState<SourceDocument[]>([]);
  const [documentId, setDocumentId] = useState('');
  const [manualOverride, setManualOverride] = useState(false);
  const [sourceText, setSourceText] = useState('');
  const [output, setOutput] = useState('');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [activeProvider, setActiveProvider] = useState<string | null>(null);
  const [model, setModel] = useState('');
  const [modelOptions, setModelOptions] = useState<ModelOption[]>([]);
  const [modelLoading, setModelLoading] = useState(false);
  const [provider, setProvider] = useState<string | null>(null);
  const [resultModel, setResultModel] = useState<string | null>(null);
  const [traceId, setTraceId] = useState<string | null>(null);
  const [validation, setValidation] = useState<any>(null);
  const [mapping, setMapping] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [timing, setTiming] = useState<any>(null);
  const [liveElapsed, setLiveElapsed] = useState(0);
  const [templateError, setTemplateError] = useState('');

  const loadModels = async (providerName?: string) => {
    setModelLoading(true);
    try {
      const name = providerName || activeProvider || 'ollama';
      const result = await apiClient.intelligenceProviderModels(name);
      const options = Array.isArray(result?.models) ? result.models : [];
      setModelOptions(options);
      const selected = model && options.some((item: ModelOption) => item.name === model) ? model : result?.selected_model || options[0]?.name || '';
      setModel(selected);
      setMessage(name === 'ollama' ? `Detected ${options.length} locally downloaded Ollama model${options.length === 1 ? '' : 's'}.` : `Loaded ${options.length} configured ${name} model option${options.length === 1 ? '' : 's'}.`);
    } catch (error: any) {
      setModelOptions([]);
      setMessage(error?.message || 'Unable to detect available AI models.');
    } finally { setModelLoading(false); }
  };

  useEffect(() => {
    try {
      const saved = JSON.parse(window.localStorage.getItem('careeros.cv-json-lab') || '{}');
      if (typeof saved.template === 'string') setTemplate(saved.template);
      if (typeof saved.instruction === 'string') setInstruction(saved.instruction);
      if (typeof saved.documentId === 'string') setDocumentId(saved.documentId);
      if (typeof saved.model === 'string') setModel(saved.model);
    } catch { /* ignore */ }
    void loadSource();
    void loadRuntimeModel();
  }, []);

  const loadRuntimeModel = async () => {
    try {
      const registry = await apiClient.intelligenceProviders();
      const selectedProvider = registry?.active_provider || registry?.providers?.find((p: any) => p.active && p.configured)?.provider || 'ollama';
      setActiveProvider(selectedProvider);
      await loadModels(selectedProvider);
    } catch (error: any) { setMessage(error?.message || 'Unable to load Global Intelligence provider/model state.'); }
  };

  const loadSource = async () => {
    try {
      const result = await apiClient.get<any>('/api/v1/developer/cv-json-lab/source');
      const docs = Array.isArray(result?.documents) ? result.documents : [];
      setSources(docs);
      const preferred = documentId && docs.some((doc: SourceDocument) => doc.id === documentId) ? documentId : result?.selected_document_id || docs[0]?.id || '';
      setDocumentId(preferred);
      setMessage(docs.length ? `Detected ${docs.length} uploaded CV${docs.length === 1 ? '' : 's'}. The latest CV is selected automatically.` : 'No uploaded CV is currently available in Document Vault.');
    } catch (error: any) { setMessage(error?.message || 'Unable to load uploaded CVs.'); }
  };

  const selectedSource = sources.find((doc) => doc.id === documentId) || sources[0] || null;
  const analysis = useMemo(() => {
    try {
      const parsed = JSON.parse(template);
      return { parsed, valid: !!parsed && typeof parsed === 'object' && !Array.isArray(parsed), chars: template.length, compactChars: compact(parsed).length, sections: sections(parsed), paths: paths(parsed) };
    } catch (error: any) { return { parsed: null, valid: false, chars: template.length, compactChars: 0, sections: [], paths: [], error: error?.message || 'Invalid JSON' }; }
  }, [template]);
  const instructionStats = useMemo(() => ({ chars: instruction.length, words: instruction.trim() ? instruction.trim().split(/\s+/).length : 0 }), [instruction]);

  useEffect(() => {
    if (!busy) return;
    const started = performance.now();
    const timer = window.setInterval(() => setLiveElapsed(performance.now() - started), 100);
    return () => window.clearInterval(timer);
  }, [busy]);

  const runTest = async () => {
    setMessage(''); setOutput(''); setValidation(null); setMapping(null); setMetrics(null); setTiming(null); setTemplateError(''); setLiveElapsed(0);
    if (!analysis.valid) { setTemplateError(analysis.error || 'JSON contract must be a valid top-level object.'); return; }
    if (!documentId && !selectedSource) { setMessage('No uploaded CV is available in Document Vault. Upload it through the normal application first.'); return; }
    if (manualOverride && !sourceText.trim()) { setMessage('Debug override is enabled but no CV text was supplied. Disable override to use the actual uploaded CV.'); return; }
    if (!model) { setMessage('Select an AI model before running the lab.'); return; }
    setBusy(true);
    const clientStarted = performance.now();
    try {
      const result = await apiClient.post<any>('/api/v1/developer/cv-json-lab/extract', {
        document_id: documentId || null,
        instruction,
        template: analysis.parsed,
        model,
        cv_text_override: manualOverride ? sourceText : null,
      });
      const clientElapsed = performance.now() - clientStarted;
      setOutput(String(result?.output || '')); setProvider(result?.provider || null); setResultModel(result?.model || null); setTraceId(result?.trace_id || null); setValidation(result?.validation || null); setMapping(result?.application_mapping || null); setMetrics(result?.metrics || null); setTiming({ ...(result?.timing || {}), browser_end_to_end_ms: Number(clientElapsed.toFixed(1)) });
      setMessage(`Extraction completed from ${result?.source_mode === 'debug_override' ? 'the debug CV text override' : 'the actual uploaded CV in Document Vault'}. The canonical CareerOS mapping path was exercised inside a rollback savepoint; the real Professional Profile was not changed.`);
    } catch (error: any) { const clientElapsed = performance.now() - clientStarted; setTiming({ browser_end_to_end_ms: Number(clientElapsed.toFixed(1)) }); setMessage(error?.message || 'CV JSON extraction failed.'); }
    finally { setBusy(false); }
  };

  const saveLocally = () => { window.localStorage.setItem('careeros.cv-json-lab', JSON.stringify({ template, instruction, documentId, model })); setMessage('JSON contract, instruction, source selection and model saved locally.'); };
  const resetDefaults = () => { setTemplate(DEFAULT_TEMPLATE); setInstruction(DEFAULT_INSTRUCTION); setMessage('Default production-shaped compact JSON contract restored.'); };

  return <CareerOSShell>
    <PageHeader eyebrow="Project Control · Intelligence · Developer Lab" title="CV JSON Extraction Lab" description="Application-level replica of CV reconciliation: use the uploaded CV from Document Vault, choose a detected AI model, send the editable JSON contract and short instruction through Global Intelligence, receive compact JSON, and exercise the normal CareerOS profile mapper without committing it." action={<Badge tone="blue">DRY RUN · NO PROFILE COMMIT</Badge>} />
    {message && <div className="mb-5 rounded-xl border bg-card px-4 py-3 text-sm">{message}</div>}

    <div className="grid gap-5 xl:grid-cols-2">
      <Card>
        <p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">1 · Actual output contract</p><h2 className="mt-2 text-lg font-bold">JSON format sent to AI</h2><p className="mt-1 text-sm text-muted-foreground">The editable JSON object is compacted before transport and converted into the provider structured-output contract.</p>
        <div className="mt-3 flex flex-wrap gap-2">{analysis.sections.map((section) => <Badge key={section} tone="blue">{section}</Badge>)}</div>
        <textarea value={template} onChange={(e) => setTemplate(e.target.value)} spellCheck={false} className="mt-4 min-h-[430px] w-full rounded-xl border bg-background p-4 font-mono text-xs leading-5" />
        {templateError && <p className="mt-2 text-sm text-destructive">{templateError}</p>}
        <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4"><Stat label="Entered chars" value={analysis.chars.toLocaleString()} /><Stat label="Compact chars" value={analysis.compactChars.toLocaleString()} /><Stat label="Sections" value={String(analysis.sections.length)} /><Stat label="Fields / paths" value={String(analysis.paths.length)} /></div>
      </Card>

      <Card>
        <p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">2 · Small AI instruction</p><h2 className="mt-2 text-lg font-bold">Instruction actually sent</h2><p className="mt-1 text-sm text-muted-foreground">Keep this short. The CV and JSON contract carry the data.</p>
        <textarea value={instruction} onChange={(e) => setInstruction(e.target.value)} spellCheck={false} className="mt-4 min-h-[210px] w-full rounded-xl border bg-background p-4 font-mono text-xs leading-5" />
        <div className="mt-3 flex gap-2"><Badge tone="blue">{instructionStats.chars.toLocaleString()} chars</Badge><Badge tone="muted">{instructionStats.words.toLocaleString()} words</Badge></div>
        <div className="mt-5 flex flex-wrap gap-2"><Button onClick={saveLocally}>Save Test Contract</Button><Button onClick={resetDefaults}>Restore Defaults</Button></div>
      </Card>
    </div>

    <Card className="mt-5">
      <p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">3 · AI model and Document Vault source</p><h2 className="mt-2 text-lg font-bold">Runtime model + uploaded CV</h2><p className="mt-1 text-sm text-muted-foreground">The provider comes from the active Global Intelligence runtime. For Ollama, the model dropdown is populated from models actually downloaded in the local Ollama instance.</p>
      <div className="mt-4 grid gap-3 md:grid-cols-[1fr_2fr_auto]">
        <div><label className="text-xs font-medium">Global Intelligence provider</label><div className="mt-1 rounded-xl border bg-muted/20 px-4 py-3 text-sm font-semibold">{activeProvider || 'Detecting…'}</div></div>
        <div><label className="text-xs font-medium">AI model</label><select value={model} onChange={(e) => setModel(e.target.value)} disabled={modelLoading || !modelOptions.length} className="mt-1 w-full rounded-xl border bg-background px-4 py-3 text-sm">{!modelOptions.length && <option value="">{modelLoading ? 'Detecting models…' : 'No model detected'}</option>}{modelOptions.map((item) => <option key={item.name} value={item.name}>{item.name}{item.parameter_size ? ` · ${item.parameter_size}` : ''}{item.source === 'ollama_local' ? ' · local' : ''}</option>)}</select><p className="mt-1 text-[11px] text-muted-foreground">Selected model is sent to the Global Intelligence runtime for this lab run; it does not change the saved provider configuration.</p></div>
        <div className="flex items-end"><Button onClick={() => loadModels()} disabled={modelLoading}>{modelLoading ? 'Detecting…' : 'Refresh Models'}</Button></div>
      </div>
      <div className="mt-4 flex flex-wrap gap-3"><select value={documentId} onChange={(e) => setDocumentId(e.target.value)} className="min-w-[360px] rounded-xl border bg-background px-4 py-3 text-sm">{!sources.length && <option value="">No uploaded CV found</option>}{sources.map((doc) => <option key={doc.id} value={doc.id}>{doc.filename} · {doc.chars.toLocaleString()} chars</option>)}</select><Button onClick={loadSource}>Refresh Uploaded CVs</Button>{selectedSource && <Badge tone="good">{selectedSource.chars.toLocaleString()} chars</Badge>}{selectedSource && <Badge tone="muted">{selectedSource.words.toLocaleString()} words</Badge>}</div>
      <div className="mt-4 rounded-xl border bg-muted/20 p-4"><p className="text-xs font-bold uppercase tracking-[.14em] text-muted-foreground">Application path</p><p className="mt-2 text-sm leading-6">Document Vault → extracted_text → compact JSON request envelope → Global Intelligence → selected model → compact JSON output → CareerOS parser/normalizer → canonical profile mapping (rollback).</p></div>
      <label className="mt-4 flex items-center gap-2 text-sm"><input type="checkbox" checked={manualOverride} onChange={(e) => setManualOverride(e.target.checked)} />Enable debug CV text override</label>
      {manualOverride && <textarea value={sourceText} onChange={(e) => setSourceText(e.target.value)} spellCheck={false} className="mt-3 min-h-[240px] w-full rounded-xl border bg-background p-4 font-mono text-xs leading-5" placeholder="Optional debug CV text. Normal mode never uses this box." />}
      <div className="mt-4 flex items-center justify-between gap-4"><p className="text-xs text-muted-foreground">Debug override is explicitly opt-in. It never modifies Document Vault. Normal mode always uses the actual uploaded CV.</p><Button onClick={runTest} disabled={busy || !analysis.valid || (!documentId && !selectedSource) || !model}>{busy ? `AI replying… ${fmtDuration(liveElapsed)}` : 'Run CV Reconciliation Lab'}</Button></div>
    </Card>

    <Card className="mt-5">
      <div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">4 · Only result</p><h2 className="mt-2 text-lg font-bold">CV JSON outcome</h2></div><div className="flex flex-wrap gap-2">{provider && <Badge tone="good">{provider}</Badge>}{resultModel && <Badge tone="blue">{resultModel}</Badge>}{traceId && <Badge tone="muted">trace {traceId.slice(0, 8)}</Badge>}{validation && <Badge tone={validation.valid_json && !validation.missing_sections?.length ? 'good' : 'warn'}>{validation.valid_json ? 'VALID JSON' : 'INVALID JSON'}</Badge>}</div></div>
      {timing && <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4"><Stat label="AI generation" value={fmtDuration(timing.ai_generation_ms)} /><Stat label="Gateway attempt" value={fmtMs(timing.gateway_attempt_ms)} /><Stat label="Backend total" value={fmtMs(timing.backend_end_to_end_ms)} /><Stat label="Browser total" value={fmtMs(timing.browser_end_to_end_ms)} /></div>}
      {timing?.native_provider_duration_ms != null && <p className="mt-2 text-[11px] text-muted-foreground">AI generation uses the provider-native generation duration when Ollama supplies it; gateway/backend timings include application transport and routing overhead.</p>}
      {validation?.missing_sections?.length ? <p className="mt-3 text-sm text-destructive">Missing contract sections: {validation.missing_sections.join(', ')}</p> : null}
      <textarea value={output} readOnly placeholder="The AI's compact CV JSON outcome will appear here..." className="mt-4 min-h-[500px] w-full rounded-xl border bg-background p-4 font-mono text-xs leading-5" />
      {metrics && <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6"><Stat label="CV chars" value={String(metrics.cv_chars)} /><Stat label="Instruction" value={String(metrics.instruction_chars)} /><Stat label="JSON compact" value={String(metrics.compact_template_chars)} /><Stat label="Prompt" value={String(metrics.prompt_chars)} /><Stat label="Output" value={String(metrics.output_chars)} /><Stat label="Employment" value={String(mapping?.would_apply?.experiences || 0)} /></div>}
      {mapping && <div className="mt-4 rounded-xl border bg-muted/20 p-4 text-sm">Canonical CareerOS mapping check: <strong>profile mutation = false</strong>. The returned compact JSON was passed through the same normalization/persistence mapper inside a rollback savepoint.</div>}
    </Card>
  </CareerOSShell>;
}

function Stat({ label, value }: { label: string; value: string }) { return <div className="rounded-xl border bg-muted/20 px-3 py-3"><p className="text-[10px] font-bold uppercase tracking-[.14em] text-muted-foreground">{label}</p><p className="mt-1 text-sm font-semibold">{value}</p></div>; }
