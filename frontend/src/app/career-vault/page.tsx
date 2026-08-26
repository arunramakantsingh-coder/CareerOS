'use client';

import { useCallback, useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import {
    CareerOSShell,
    Card,
    PageHeader,
    Button,
    Badge
} from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';

export default function CareerVault() {
    const [p, setP] = useState<any>({});
    const [evidence, setEvidence] = useState<any[]>([]);
    const [msg, setMsg] = useState('');
    const [busy, setBusy] = useState(false);

    /*
     * IMPORTANT:
     * This function is async, so it returns a Promise.
     * It must NEVER be passed directly to useEffect().
     */
    const load = useCallback(async () => {
        try {
            const [x, y] = await Promise.all([
                apiClient.profile(),
                apiClient.evidence()
            ]);

            setP(x.profile || {});
            setEvidence(y);
        } catch (err: any) {
            setMsg(err?.message || 'Unable to load Career Vault.');
        }
    }, []);

    /*
     * React effects must return either:
     *   - nothing / undefined
     *   - a synchronous cleanup function
     *
     * We deliberately call the async function without returning it.
     */
    useEffect(() => {
        void load();
    }, [load]);

    const save = async (e: FormEvent) => {
        e.preventDefault();
        setBusy(true);

        try {
            await apiClient.saveProfile({
                ...p,
                target_roles: (p.target_roles || []).filter(Boolean),
                preferred_locations: (p.preferred_locations || []).filter(Boolean),
                industries: (p.industries || []).filter(Boolean)
            });

            setMsg('Career profile saved.');
            await load();
        } catch (err: any) {
            setMsg(err?.message || 'Unable to save Career Vault.');
        } finally {
            setBusy(false);
        }
    };

    const add = async () => {
        const claim = prompt(
            'Enter a verified career fact or achievement:'
        );

        if (!claim) {
            return;
        }

        try {
            await apiClient.addEvidence({
                claim,
                source_type: 'user',
                confidence: 1
            });

            setMsg('Verified evidence added.');
            await load();
        } catch (err: any) {
            setMsg(err?.message || 'Unable to add evidence.');
        }
    };

    return (
        <CareerOSShell>
            <PageHeader
                eyebrow="Career"
                title="Career Vault"
                description="Your verified professional source of truth. AI may tailor positioning, but it must not invent career facts."
                action={
                    <Button onClick={add}>
                        Add verified evidence
                    </Button>
                }
            />

            <form
                onSubmit={save}
                className="grid gap-4 lg:grid-cols-2"
            >
                <Card title="Career identity">
                    <div className="space-y-4">
                        <Field
                            label="Name"
                            value={p.name || ''}
                            onChange={(v) =>
                                setP({ ...p, name: v })
                            }
                        />

                        <Field
                            label="Professional summary"
                            value={p.description || ''}
                            onChange={(v) =>
                                setP({ ...p, description: v })
                            }
                            area
                        />

                        <Field
                            label="Target roles (comma separated)"
                            value={(p.target_roles || []).join(', ')}
                            onChange={(v) =>
                                setP({
                                    ...p,
                                    target_roles: v
                                        .split(',')
                                        .map((x: string) => x.trim())
                                })
                            }
                        />

                        <Field
                            label="Seniority"
                            value={p.seniority || ''}
                            onChange={(v) =>
                                setP({ ...p, seniority: v })
                            }
                        />

                        <Field
                            label="Years of experience"
                            value={p.years_experience ?? ''}
                            onChange={(v) =>
                                setP({
                                    ...p,
                                    years_experience: v
                                        ? Number(v)
                                        : null
                                })
                            }
                            type="number"
                        />
                    </div>
                </Card>

                <Card title="Preferences">
                    <div className="space-y-4">
                        <Field
                            label="Preferred locations"
                            value={(p.preferred_locations || []).join(', ')}
                            onChange={(v) =>
                                setP({
                                    ...p,
                                    preferred_locations: v
                                        .split(',')
                                        .map((x: string) => x.trim())
                                })
                            }
                        />

                        <Field
                            label="Remote preference"
                            value={p.remote_preference || ''}
                            onChange={(v) =>
                                setP({
                                    ...p,
                                    remote_preference: v
                                })
                            }
                        />

                        <Field
                            label="Industries"
                            value={(p.industries || []).join(', ')}
                            onChange={(v) =>
                                setP({
                                    ...p,
                                    industries: v
                                        .split(',')
                                        .map((x: string) => x.trim())
                                })
                            }
                        />

                        <Button disabled={busy}>
                            {busy
                                ? 'Saving...'
                                : 'Save Career Vault'}
                        </Button>

                        {msg && (
                            <p className="text-sm text-muted-foreground">
                                {msg}
                            </p>
                        )}
                    </div>
                </Card>
            </form>

            <div className="mt-6">
                <Card
                    title={`Verified evidence · ${evidence.length}`}
                >
                    <div className="space-y-3">
                        {evidence.length ? (
                            evidence.map((x: any) => (
                                <div
                                    key={x.id}
                                    className="rounded-lg border p-4"
                                >
                                    <div className="flex items-start justify-between gap-3">
                                        <p className="text-sm font-medium">
                                            {x.claim}
                                        </p>

                                        <Badge tone="good">
                                            Verified
                                        </Badge>
                                    </div>

                                    <p className="mt-1 text-xs text-muted-foreground">
                                        Source: {x.source_type || 'user'} ·
                                        confidence{' '}
                                        {Math.round(
                                            (x.confidence ?? 1) * 100
                                        )}
                                        %
                                    </p>
                                </div>
                            ))
                        ) : (
                            <p className="text-sm text-muted-foreground">
                                No evidence yet. Add facts,
                                achievements, projects or metrics
                                that you can substantiate.
                            </p>
                        )}
                    </div>
                </Card>
            </div>
        </CareerOSShell>
    );
}

function Field({
    label,
    value,
    onChange,
    area,
    type = 'text'
}: {
    label: string;
    value: any;
    onChange: (v: string) => void;
    area?: boolean;
    type?: string;
}) {
    return (
        <label className="block text-sm font-medium">
            {label}

            {area ? (
                <textarea
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    rows={4}
                    className="mt-1 w-full rounded-lg border px-3 py-2.5"
                />
            ) : (
                <input
                    type={type}
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    className="mt-1 w-full rounded-lg border px-3 py-2.5"
                />
            )}
        </label>
    );
}
