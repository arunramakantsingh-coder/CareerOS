"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { resolveApiBaseUrl } from "@/lib/api/client";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try { await login(email, password); }
    catch (err: any) { setError(err.message || "Login failed. Please try again."); }
    finally { setIsLoading(false); }
  };

  const oauth = (provider: "google" | "linkedin") => {
    window.location.href = `${resolveApiBaseUrl()}/api/v1/auth/oauth/${provider}/start`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4 py-12">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center"><div className="mx-auto grid h-12 w-12 place-items-center rounded-xl bg-primary text-2xl font-bold text-primary-foreground">◈</div><h1 className="mt-5 text-3xl font-bold">Sign in to CareerOS</h1><p className="mt-2 text-sm text-muted-foreground">Evidence-first career intelligence for your professional life.</p><p className="mt-3 text-sm text-muted-foreground">Or <Link href="/register" className="font-semibold text-primary">create a new account</Link></p></div>
        <form className="space-y-5" onSubmit={handleSubmit}>
          {error && <div className="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-800 dark:bg-red-950/30 dark:text-red-200">{error}</div>}
          <div className="space-y-3"><input id="email" name="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="block w-full rounded-lg border bg-background px-3 py-3 text-sm outline-none focus:border-primary" placeholder="Email address" /><input id="password" name="password" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} className="block w-full rounded-lg border bg-background px-3 py-3 text-sm outline-none focus:border-primary" placeholder="Password" /></div>
          <button type="submit" disabled={isLoading} className="w-full rounded-lg bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground disabled:opacity-50">{isLoading ? "Signing in…" : "Sign in"}</button>
        </form>
        <div className="relative"><div className="absolute inset-0 flex items-center"><div className="w-full border-t" /></div><div className="relative flex justify-center"><span className="bg-background px-3 text-xs text-muted-foreground">OR CONTINUE WITH</span></div></div>
        <div className="grid grid-cols-2 gap-3"><button type="button" onClick={() => oauth("google")} className="rounded-lg border bg-card px-4 py-3 text-sm font-semibold hover:bg-muted">Google</button><button type="button" onClick={() => oauth("linkedin")} className="rounded-lg border bg-card px-4 py-3 text-sm font-semibold hover:bg-muted">LinkedIn</button></div>
        <p className="text-center text-[11px] text-muted-foreground">Provider login and external-data authorization are separate. CareerOS only requests the scopes needed for the selected flow.</p>
      </div>
    </div>
  );
}
