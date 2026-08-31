"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { CareerOSShell, Card, PageHeader, Badge, Button } from "@/components/CareerOSShell";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function OnboardingPage() {
  const { user, token, isAuthenticated, isLoading } = useAuth(); const router = useRouter();
  const [profile, setProfile] = useState<any>(null); const [profileLoading, setProfileLoading] = useState(true); const [message,setMessage]=useState("");
  useEffect(() => { if (!isLoading && !isAuthenticated) router.push("/login"); }, [isLoading, isAuthenticated, router]);
  useEffect(() => { if (isAuthenticated && token) fetchProfile(); }, [isAuthenticated, token]);
  const fetchProfile = async () => { try { const response = await fetch(`${API_URL}/api/v1/profile/`, { headers: { Authorization: `Bearer ${token}` } }); if (response.ok) setProfile(await response.json()); else if (response.status===404) setProfile(null); } catch { setMessage("Unable to load profile setup state."); } finally { setProfileLoading(false); } };
  const createProfile = async () => { try { const response = await fetch(`${API_URL}/api/v1/profile/`, { method:"POST", headers:{"Content-Type":"application/json",Authorization:`Bearer ${token}`}, body:JSON.stringify({user_id:user?.id,full_name:user?.name||"",primary_email:user?.email||""}) }); if(response.ok) setProfile(await response.json()); else setMessage("Unable to create your profile."); } catch { setMessage("Unable to create your profile."); } };

  if (isLoading || profileLoading) return <div className="grid min-h-screen place-items-center bg-background text-foreground">Loading profile setup…</div>;
  if (!isAuthenticated) return null;

  const score=Number(profile?.completeness_score||0);
  return <CareerOSShell>
    <PageHeader eyebrow="Profile · Setup" title="Build your professional identity" description="CareerOS starts with evidence. Connect identity sources, add your CV and professional documents, then review and complete anything the system cannot confidently derive." action={<Badge tone={score>=80?'good':'blue'}>{score}% complete</Badge>} />
    {message&&<div className="mb-4 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm">{message}</div>}
    <div className="grid gap-4 lg:grid-cols-[1.2fr_.8fr]">
      <Card title="Recommended setup sequence" className="techno-glow">
        <div className="space-y-3">
          {[
            ['1','Identity & connections','Confirm your primary email, phone and LinkedIn identity.','/profile'],
            ['2','Upload your CV','Keep CV / Resume intake independent and first-class.','/documents#cv'],
            ['3','Add professional evidence','Bulk files, folders, ZIP and camera intake populate the evidence vault.','/documents#vault'],
            ['4','Review Profile Intelligence','Check extracted experience, skills, certifications and provenance.','/profile/intelligence'],
            ['5','Complete missing information','Edit anything missing or incorrect before job discovery.','/profile'],
          ].map(([n,title,desc,href])=><Link key={n} href={href} className="flex gap-4 rounded-xl border bg-background/35 p-4 transition hover:border-primary/40 hover:bg-primary/5"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-primary/10 text-sm font-bold text-primary">{n}</span><span><span className="block text-sm font-semibold">{title}</span><span className="mt-1 block text-xs leading-5 text-muted-foreground">{desc}</span></span></Link>)}
        </div>
      </Card>
      <div className="space-y-4">
        <Card title="Current identity"><div className="space-y-4"><div><p className="text-xs text-muted-foreground">Name</p><p className="font-semibold">{profile?.full_name||user?.name||'Not set'}</p></div><div><p className="text-xs text-muted-foreground">Primary email</p><p className="font-semibold break-all">{profile?.primary_email||user?.email||'Not set'}</p></div><div><p className="text-xs text-muted-foreground">Professional title</p><p className="font-semibold">{profile?.title||'Not set'}</p></div>{!profile&&<Button onClick={createProfile}>Create profile foundation</Button>}</div></Card>
        <Card title="Why this exists"><p className="text-sm leading-6 text-muted-foreground">Setup is part of Profile, not a separate application universe. You can return here anytime; login now goes directly to the Dashboard.</p></Card>
      </div>
    </div>
  </CareerOSShell>;
}
