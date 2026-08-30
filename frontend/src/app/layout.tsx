import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { AuthProvider } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'CareerOS — Global Career Operating System',
  description: 'Your evidence-first AI career workspace.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en" suppressHydrationWarning><body className={inter.className}>
    <ThemeProvider><AuthProvider><main className="min-h-screen bg-background">{children}</main></AuthProvider></ThemeProvider>
  </body></html>;
}
