'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
export default function OnboardingPage(){const router=useRouter();useEffect(()=>{router.replace('/profile/setup')},[router]);return <div className="grid min-h-screen place-items-center bg-background text-sm text-muted-foreground">Opening Profile Setup…</div>}
