'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ProfessionalDocumentsPage(){
 const router=useRouter();
 useEffect(()=>{router.replace('/evidence-library')},[router]);
 return <div className="grid min-h-screen place-items-center bg-background text-sm text-muted-foreground">Opening Evidence Library…</div>;
}
