"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { resolveApiBaseUrl } from "@/lib/api/client";
import { useTheme, type CareerOSTheme } from "@/contexts/ThemeContext";

const themes: Array<{ key: CareerOSTheme; label: string }> = [
  { key: "light", label: "Light" }, { key: "dark", label: "Dark" }, { key: "techno", label: "Command" }
];

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const { theme, setTheme } = useTheme();
  const api = resolveApiBaseUrl();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("oauth") === "error") setError(params.get("message") || "OAuth sign-in could not be completed.");
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setError(""); setIsLoading(true);
    try { await login(email, password); }
    catch (err: any) { setError(err?.message || "Login failed. Please try again."); }
    finally { setIsLoading(false); }
  };

  return <main className="relative min-h-screen overflow-hidden bg-background text-foreground">
    <div className="pointer-events-none absolute inset-0 opacity-60"><div className="absolute left-[-12rem] top-[-10rem] h-[32rem] w-[32rem] rounded-full bg-primary/10 blur-3xl"/><div className="absolute bottom-[-12rem] right-[-8rem] h-[28rem] w-[28rem] rounded-full bg-primary/10 blur-3xl"/></div>
    <div className="relative mx-auto flex min-h-screen w-full max-w-6xl items-center justify-center px-4 py-8 lg:grid lg:grid-cols-[1.05fr_.95fr] lg:gap-14">
      <section className="hidden lg:block"><div className="mb-8 flex items-center gap-3"><span className="grid h-12 w-12 place-items-center rounded-2xl bg-primary text-xl font-bold text-primary-foreground shadow-[0_0_30px_hsl(var(--primary)/.25)]">◇</span><div><p className="text-lg font-bold">CareerOS</p><p className="text-xs text-muted-foreground">AI-powered global career operating system</p></div></div><p className="text-sm font-semibold uppercase tracking-[.18em] text-primary">Evidence-first career intelligence</p><h1 className="mt-3 max-w-2xl text-5xl font-bold leading-tight">Build your professional identity once. Let CareerOS carry it forward.</h1><p className="mt-5 max-w-xl text-base leading-7 text-muted-foreground">Connect your identity, import your CV, preserve professional evidence and build a canonical career profile that can power discovery, applications and interview workflows.</p><div className="mt-8 grid max-w-xl gap-3 sm:grid-cols-3">{[["01","Identity","Google / LinkedIn"],["02","Evidence","CV + document vault"],["03","Profile","Editable + traceable"]].map(([n,t,d])=><div key={n} className="rounded-xl border bg-card/60 p-4 backdrop-blur"><p className="text-xs font-mono text-primary">{n}</p><p className="mt-2 text-sm font-semibold">{t}</p><p className="mt-1 text-xs text-muted-foreground">{d}</p></div>)}</div></section>
      <section className="w-full max-w-md justify-self-center"><div className="mb-6 flex items-center justify-between lg:justify-end"><div className="flex items-center gap-1 rounded-xl border bg-card/70 p-1">{themes.map(t=><button key={t.key} type="button" onClick={()=>setTheme(t.key)} className={`rounded-lg px-3 py-1.5 text-[11px] font-semibold ${theme===t.key?'bg-primary text-primary-foreground':'text-muted-foreground hover:text-foreground'}`}>{t.label}</button>)}</div></div>
        <div className="rounded-2xl border bg-card/75 p-6 shadow-2xl backdrop-blur-xl sm:p-8"><div className="mb-7 text-center lg:text-left"><div className="mx-auto mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-primary text-xl font-bold text-primary-foreground lg:mx-0">◇</div><p className="text-xs font-semibold uppercase tracking-[.16em] text-primary">Welcome back</p><h2 className="mt-1 text-3xl font-bold">Sign in to CareerOS</h2><p className="mt-2 text-sm text-muted-foreground">Return to your career workspace.</p></div>{error&&<div className="mb-4 rounded-xl border border-red-500/25 bg-red-500/10 px-4 py-3 text-sm text-red-600 dark:text-red-300">{error}</div>}
          <div className="grid grid-cols-2 gap-3"><a href={`${api}/api/v1/auth/oauth/google/start`} className="rounded-xl border bg-background/60 px-4 py-3 text-center text-sm font-semibold transition hover:border-primary/50 hover:bg-muted">Continue with Google</a><a href={`${api}/api/v1/auth/oauth/linkedin/start`} className="rounded-xl border bg-background/60 px-4 py-3 text-center text-sm font-semibold transition hover:border-primary/50 hover:bg-muted">Continue with LinkedIn</a></div>
          <div className="mt-3 rounded-xl border border-primary/15 bg-primary/5 px-3 py-2 text-[11px] leading-5 text-muted-foreground">Provider buttons navigate directly to CareerOS OAuth. Gmail mailbox access is intentionally a separate readonly connection after sign-in.</div>
          <div className="my-6 flex items-center gap-3"><div className="h-px flex-1 bg-border"/><span className="text-[11px] uppercase tracking-wider text-muted-foreground">or email</span><div className="h-px flex-1 bg-border"/></div>
          <form onSubmit={handleSubmit} className="space-y-4"><label className="block"><span className="text-xs font-medium text-muted-foreground">Email address</span><input id="email" name="email" type="email" autoComplete="email" required value={email} onChange={e=>setEmail(e.target.value)} className="mt-1.5 w-full rounded-xl border bg-background px-3.5 py-3 text-sm outline-none transition focus:border-primary" placeholder="you@example.com"/></label><label className="block"><span className="text-xs font-medium text-muted-foreground">Password</span><input id="password" name="password" type="password" autoComplete="current-password" required value={password} onChange={e=>setPassword(e.target.value)} className="mt-1.5 w-full rounded-xl border bg-background px-3.5 py-3 text-sm outline-none transition focus:border-primary" placeholder="••••••••"/></label><button type="submit" disabled={isLoading} className="w-full rounded-xl bg-primary px-4 py-3 text-sm font-bold text-primary-foreground shadow-sm transition hover:opacity-90 disabled:opacity-50">{isLoading?"Signing in…":"Sign in"}</button></form>
          <p className="mt-6 text-center text-sm text-muted-foreground">New to CareerOS? <Link href="/register" className="font-semibold text-primary hover:underline">Create your account</Link></p><Link href="/settings#connections" className="mt-5 block text-center text-xs font-semibold text-primary hover:underline">Already signed in? Manage Google, Gmail & LinkedIn connections →</Link>
        </div>
      </section>
    </div>
  </main>;
}
