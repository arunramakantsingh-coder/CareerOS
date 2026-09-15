'use client';

import { useEffect, useMemo, useState } from 'react';
import { CareerOSShell, PageHeader, Card, Badge, Button } from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';

const DEFAULT_TEMPLATE = `{
  "profile": {
    "full_name": null,
    "title": null,
    "summary": null,
    "location": null,
    "email": null,
    "phone": null,
    "linkedin": null
  },
  "employment": [
    {
      "title": "",
      "employer": "",
      "client": null,
      "start_date": null,
      "end_date": null
    }
  ],
  "education": [
    {
      "institution": "",
      "degree": "",
      "field_of_study": null,
      "start_date": null,
      "end_date": null
    }
  ],
  "certifications": [
    {
      "name": "",
      "issuer": null,
      "issue_date": null,
      "expiry_date": null
    }
  ],
  "skills": [],
  "projects": [],
  "accomplishments": []
}`;

const DEFAULT_INSTRUCTION = `Extract the CV into the exact JSON structure provided below.
The CV is the only source of truth. Never invent information.
Preserve every genuine employment role separately; never merge separate roles at the same employer.
Keep skills, certifications, education, projects and accomplishments in their own sections.
Return JSON only. Do not return markdown, commentary, recommendations, personas or career advice.`;

function compactJson(value: unknown) {
  return JSON.stringify(value);
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

function topLevelSections(value: unknown): string[] {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return [];
  return Object.keys(value as Record<string, unknown>);
}

export default function CvJsonLab() {
  const [template, setTemplate] = useState(DEFAULT_TEMPLATE);
  const [instruction, setInstruction] = useState(DEFAULT_INSTRUCTION);
  const [cvText, setCvText] = useState('');
  const [output, setOutput] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [provider, setProvider] = useState<string | null>(null);
  const [model, setModel] = useState<string | null>(null);
  const [templateError, setTemplateError] = useState('');

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem('careeros.cv-json-lab');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (typeof parsed.template === 'string') setTemplate(parsed.template);
        if (typeof parsed.instruction === 'string') setInstruction(parsed.instruction);
      }
    } catch { /* ignore invalid local test state */ }
  }, []);

  const analysis = useMemo(() => {
    try {
      const parsed = JSON.parse(template);
      const compact = compactJson(parsed);
      const paths = collectPaths(parsed);
      return {
        parsed,
        compact,
        valid: true,
        chars: template.length,
        compactChars: compact.length,
        sections: topLevelSections(parsed),
        paths,
      };
    } catch (error: any) {
      return { parsed: null, compact: '', valid: false, chars: template.length, compactChars: 0, sections: [], paths: [], error: error?.message || 'Invalid JSON' };
    }
  }, [template]);

  const instructionStats = useMemo(() => ({
    chars: instruction.length,
    words: instruction.trim() ? instruction.trim().split(/\s+/).length : 0,
  }), [instruction]);

  const cvStats = useMemo(() => ({
    chars: cvText.length,
    words: cvText.trim() ? cvText.trim().split(/\s+/).length : 0,
  }), [cvText]);

  const estimatedInputChars = instruction.length + analysis.compactChars + cvText.length;
  const estimatedInputTokens = Math.ceil(estimatedInputChars / 4);

  const saveLocally = () => {
    window.localStorage.setItem('careeros.cv-json-lab', JSON.stringify({ template, instruction }));
    setMessage('Template and instruction saved locally in this browser.');
  };

  const resetDefaults = () => {
    setTemplate(DEFAULT_TEMPLATE);
    setInstruction(DEFAULT_INSTRUCTION);
    setMessage('Default compact extraction template restored.');
  };

  const runTest = async () => {
    setMessage('');
    setOutput('');
    setTemplateError('');
    if (!analysis.valid) {
      setTemplateError(analysis.error || 'JSON template is invalid.');
      return;
    }
    if (!cvText.trim()) {
      setMessage('Paste the extracted CV text before running the test.');
      return;
    }
    setBusy(true);
    const prompt = `${instruction.trim()}\n\nTARGET JSON STRUCTURE (template; preserve these keys and nesting):\n${analysis.compact}\n\nSOURCE CV:\n${cvText}`;
    try {
      const result = await apiClient.post<any>('/api/v1/intelligence/generate', {
        prompt,
        temperature: 0,
      });
      const response = String(result?.response || '').trim();
      setOutput(response);
      setProvider(result?.provider || result?.routing?.selected_provider || null);
      setModel(result?.model || result?.routing?.selected_model || null);
      setMessage('Extraction test completed. The result was returned without modifying the Professional Profile.');
    } catch (error: any) {
      setMessage(error?.message || 'Extraction test failed.');
    } finally {
      setBusy(false);
    }
  };

  const validateOutput = useMemo(() => {
    if (!output.trim()) return null;
    try {
      const parsed = JSON.parse(output);
      const expected = analysis.sections;
      const actual = topLevelSections(parsed);
      const missing = expected.filter((key) => !actual.includes(key));
      return { valid: true, actual, missing };
    } catch (error: any) {
      return { valid: false, actual: [], missing: [], error: error?.message || 'Output is not valid JSON' };
    }
  }, [output, analysis.sections]);

  return (
    <CareerOSShell>
      <PageHeader
        eyebrow="Project Control · Intelligence · Developer Lab"
        title="CV JSON Extraction Lab"
        description="Developer-only sandbox for testing compact CV extraction instructions and JSON templates against the active Global Intelligence provider. Nothing in this lab writes to the Professional Profile."
        action={<Badge tone="blue">NO PROFILE MUTATION</Badge>}
      />

      {message && <div className="mb-5 rounded-xl border bg-card px-4 py-3 text-sm">{message}</div>}

      <div className="grid gap-5 xl:grid-cols-2">
        <Card>
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">1 · Output contract</p>
              <h2 className="mt-2 text-lg font-bold">JSON format / compact template</h2>
              <p className="mt-1 text-sm text-muted-foreground">Paste the exact JSON shape you want the AI to return. This is treated as a template, not as CV data.</p>
            </div>
            <Badge tone={analysis.valid ? 'good' : 'warn'}>{analysis.valid ? 'VALID JSON' : 'INVALID JSON'}</Badge>
          </div>
          <textarea value={template} onChange={(e) => setTemplate(e.target.value)} spellCheck={false} className="mt-4 min-h-[430px] w-full rounded-xl border bg-background p-4 font-mono text-xs leading-5 outline-none focus:ring-2 focus:ring-primary/30" />
          {templateError && <p className="mt-2 text-sm text-destructive">{templateError}</p>}
          <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
            <Stat label="Chars" value={analysis.chars.toLocaleString()} />
            <Stat label="Compact" value={analysis.compactChars.toLocaleString()} />
            <Stat label="Sections" value={String(analysis.sections.length)} />
            <Stat label="Fields / paths" value={String(analysis.paths.length)} />
          </div>
        </Card>

        <Card>
          <div>
            <p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">2 · AI instruction</p>
            <h2 className="mt-2 text-lg font-bold">Small extraction instruction</h2>
            <p className="mt-1 text-sm text-muted-foreground">Keep this short. The CV and JSON template carry the data contract.</p>
          </div>
          <textarea value={instruction} onChange={(e) => setInstruction(e.target.value)} spellCheck={false} className="mt-4 min-h-[210px] w-full rounded-xl border bg-background p-4 font-mono text-xs leading-5 outline-none focus:ring-2 focus:ring-primary/30" />
          <div className="mt-3 flex flex-wrap gap-2"><Badge tone="blue">{instructionStats.chars.toLocaleString()} chars</Badge><Badge tone="muted">{instructionStats.words.toLocaleString()} words</Badge></div>
          <div className="mt-5 rounded-xl border bg-muted/20 p-4">
            <p className="text-xs font-bold uppercase tracking-[.14em] text-muted-foreground">Detected sections</p>
            <div className="mt-3 flex flex-wrap gap-2">{analysis.sections.map((section) => <Badge key={section} tone="blue">{section}</Badge>)}</div>
            {!analysis.sections.length && <p className="mt-2 text-sm text-muted-foreground">A top-level JSON object is required.</p>}
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button onClick={saveLocally}>Save Template Locally</Button>
            <Button onClick={resetDefaults}>Restore Defaults</Button>
          </div>
        </Card>
      </div>

      <Card className="mt-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">3 · Source document</p>
            <h2 className="mt-2 text-lg font-bold">CV text input</h2>
            <p className="mt-1 text-sm text-muted-foreground">Paste extracted CV text here for repeatable provider/model benchmarking.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge tone="blue">{cvStats.chars.toLocaleString()} chars</Badge>
            <Badge tone="muted">{cvStats.words.toLocaleString()} words</Badge>
            <Badge tone="muted">~{estimatedInputTokens.toLocaleString()} input tokens</Badge>
          </div>
        </div>
        <textarea value={cvText} onChange={(e) => setCvText(e.target.value)} spellCheck={false} placeholder="Paste the extracted CV text here..." className="mt-4 min-h-[360px] w-full rounded-xl border bg-background p-4 font-mono text-xs leading-5 outline-none focus:ring-2 focus:ring-primary/30" />
        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-muted-foreground">Estimated input size = instruction + compact JSON template + CV. Token estimate is approximate and model-dependent.</p>
          <Button onClick={runTest} disabled={busy || !analysis.valid || !cvText.trim()}>{busy ? 'Running AI extraction…' : 'Run AI Extraction Test'}</Button>
        </div>
      </Card>

      <Card className="mt-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">4 · Result</p>
            <h2 className="mt-2 text-lg font-bold">AI output</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {provider && <Badge tone="good">{provider}</Badge>}
            {model && <Badge tone="blue">{model}</Badge>}
            {validateOutput && <Badge tone={validateOutput.valid && !validateOutput.missing.length ? 'good' : 'warn'}>{validateOutput.valid ? `${validateOutput.actual.length} top-level sections` : 'INVALID JSON'}</Badge>}
          </div>
        </div>
        {validateOutput?.missing.length ? <p className="mt-3 text-sm text-destructive">Missing expected sections: {validateOutput.missing.join(', ')}</p> : null}
        {validateOutput && !validateOutput.valid ? <p className="mt-3 text-sm text-destructive">{validateOutput.error}</p> : null}
        <textarea value={output} readOnly placeholder="AI JSON output will appear here..." className="mt-4 min-h-[430px] w-full rounded-xl border bg-background p-4 font-mono text-xs leading-5 outline-none" />
      </Card>

      <div className="mt-5 rounded-2xl border bg-card/60 p-5">
        <p className="text-xs font-bold uppercase tracking-[.16em] text-muted-foreground">Safety boundary</p>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">This lab calls the Global Intelligence generation endpoint only. It does not reconcile, create, update or delete any Professional Profile, employment, education, certification, skill, persona or career fact. Use the normal Reconcile with AI workflow only after the extraction contract has been validated here.</p>
      </div>
    </CareerOSShell>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return <div className="rounded-xl border bg-muted/20 px-3 py-3"><p className="text-[10px] font-bold uppercase tracking-[.14em] text-muted-foreground">{label}</p><p className="mt-1 text-sm font-semibold">{value}</p></div>;
}
