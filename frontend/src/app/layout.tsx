import type { Metadata } from 'next'; import type { ReactNode } from 'react';
import './globals.css';
export const metadata: Metadata = { title: 'CareerOS — Personal Job & Interview Copilot', description: 'Evidence-first AI career operating system' };
export default function RootLayout({children}:{children:ReactNode}){return <html lang="en"><body>{children}</body></html>}
