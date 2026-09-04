"use client";

import { useEffect, useState } from "react";
import { resolveApiBaseUrl } from "@/lib/api/client";

export default function OAuthCallbackPage() {
  const [message, setMessage] = useState("Completing secure sign-in…");

  useEffect(() => {
    let active = true;

    (async () => {
      const params = new URLSearchParams(window.location.hash.replace(/^#/, ""));
      const token = params.get("access_token");
      const provider = params.get("provider") || "OAuth";

      if (!token) {
        if (active) setMessage("Sign-in could not be completed because no CareerOS token was returned.");
        window.setTimeout(() => window.location.replace("/login?oauth=error&message=Missing%20CareerOS%20access%20token"), 1200);
        return;
      }

      try {
        localStorage.setItem("access_token", token);
        localStorage.removeItem("careeros_token");

        const response = await fetch(`${resolveApiBaseUrl()}/api/v1/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
          cache: "no-store",
        });
        const user = await response.json().catch(() => null);

        if (!response.ok || !user?.id) {
          localStorage.removeItem("access_token");
          throw new Error(typeof user?.detail === "string" ? user.detail : "Unable to load the CareerOS user after OAuth sign-in.");
        }

        localStorage.setItem("user", JSON.stringify(user));
        if (active) setMessage(`${provider} sign-in complete. Opening CareerOS…`);
        window.location.replace("/");
      } catch (error: any) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        const detail = typeof error?.message === "string" ? error.message : "OAuth sign-in failed.";
        if (active) setMessage(detail);
        window.setTimeout(() => window.location.replace(`/login?oauth=error&message=${encodeURIComponent(detail)}`), 1200);
      }
    })();

    return () => { active = false; };
  }, []);

  return (
    <main className="grid min-h-screen place-items-center bg-background px-4 text-foreground">
      <div className="w-full max-w-md rounded-2xl border bg-card p-8 text-center shadow-xl">
        <div className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-primary text-primary-foreground">◇</div>
        <h1 className="mt-4 text-xl font-bold">CareerOS authentication</h1>
        <p className="mt-2 text-sm text-muted-foreground">{message}</p>
      </div>
    </main>
  );
}
