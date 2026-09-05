"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function OnboardingPage() {
  const router = useRouter();
  useEffect(() => { router.replace("/profile#personal"); }, [router]);
  return <div className="grid min-h-screen place-items-center bg-background text-foreground"><div className="rounded-2xl border bg-card px-6 py-5 text-sm text-muted-foreground">Opening Profile Setup…</div></div>;
}
