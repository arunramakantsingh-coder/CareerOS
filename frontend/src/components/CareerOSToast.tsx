'use client';

import { useEffect, useState } from 'react';

type Toast = { id: number; type: 'success' | 'error' | 'info'; message: string };

type ToastEventDetail = { type?: Toast['type']; message?: string };

export default function CareerOSToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const onToast = (event: Event) => {
      const detail = (event as CustomEvent<ToastEventDetail>).detail || {};
      if (!detail.message) return;
      const id = Date.now() + Math.random();
      setToasts(current => [...current, { id, type: detail.type || 'info', message: detail.message! }].slice(-4));
      window.setTimeout(() => setToasts(current => current.filter(toast => toast.id !== id)), 5000);
    };
    window.addEventListener('careeros:toast', onToast);
    return () => window.removeEventListener('careeros:toast', onToast);
  }, []);

  if (!toasts.length) return null;

  return (
    <div className="pointer-events-none fixed right-4 top-20 z-[100] flex w-[min(420px,calc(100vw-2rem))] flex-col gap-2">
      {toasts.map(toast => (
        <div
          key={toast.id}
          role="status"
          aria-live="polite"
          className={`pointer-events-auto rounded-xl border px-4 py-3 text-sm shadow-xl backdrop-blur ${
            toast.type === 'success'
              ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300'
              : toast.type === 'error'
                ? 'border-red-500/30 bg-red-500/10 text-red-700 dark:text-red-300'
                : 'border-primary/30 bg-card text-foreground'
          }`}
        >
          <div className="flex items-start gap-3">
            <span className="font-bold" aria-hidden="true">{toast.type === 'success' ? '✓' : toast.type === 'error' ? '✕' : '•'}</span>
            <p className="min-w-0 flex-1 leading-5">{toast.message}</p>
            <button type="button" onClick={() => setToasts(current => current.filter(item => item.id !== toast.id))} className="text-xs opacity-60 hover:opacity-100" aria-label="Dismiss notification">×</button>
          </div>
        </div>
      ))}
    </div>
  );
}
