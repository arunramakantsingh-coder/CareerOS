'use client';

import { FormEvent, useEffect, useState } from 'react';
import { Card, Button, Badge } from '@/components/CareerOSShell';
import { apiClient } from '@/lib/api/client';

type PasswordStatus = { has_password: boolean };

export default function PasswordCredentialCard() {
  const [hasPassword, setHasPassword] = useState<boolean | null>(null);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');

  const loadStatus = async () => {
    try {
      const result = await apiClient.get<PasswordStatus>('/api/v1/auth/password/status');
      setHasPassword(result.has_password);
    } catch (error: any) {
      setMessage(error?.message || 'Unable to check password status.');
    }
  };

  useEffect(() => { loadStatus(); }, []);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setMessage('');
    if (newPassword.length < 8) {
      setMessage('New password must be at least 8 characters.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setMessage('New password and confirmation do not match.');
      return;
    }

    setBusy(true);
    try {
      await apiClient.post<PasswordStatus>('/api/v1/auth/password', {
        ...(hasPassword ? { current_password: currentPassword } : {}),
        new_password: newPassword,
      });
      setHasPassword(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setMessage(hasPassword ? 'Password changed successfully.' : 'Password set successfully. You can now sign in with email and password.');
    } catch (error: any) {
      setMessage(error?.message || 'Unable to save password.');
    } finally {
      setBusy(false);
    }
  };

  if (hasPassword === null) {
    return <Card title="Password authentication"><p className="text-sm text-muted-foreground">Checking password credential status…</p></Card>;
  }

  return (
    <Card title="Password authentication">
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone={hasPassword ? 'good' : 'muted'}>{hasPassword ? 'Password configured' : 'No password configured'}</Badge>
        <span className="text-xs text-muted-foreground">{hasPassword ? 'Use this to change your local sign-in password.' : 'Your OAuth account can add a local email/password sign-in without creating a second account.'}</span>
      </div>
      <form onSubmit={submit} className="mt-4 max-w-xl space-y-3">
        {hasPassword && (
          <label className="block text-sm font-medium">Current password
            <input type="password" autoComplete="current-password" value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} className="mt-1 w-full rounded-lg border bg-background px-3 py-2.5" required />
          </label>
        )}
        <label className="block text-sm font-medium">New password
          <input type="password" autoComplete="new-password" minLength={8} value={newPassword} onChange={e => setNewPassword(e.target.value)} className="mt-1 w-full rounded-lg border bg-background px-3 py-2.5" required />
        </label>
        <label className="block text-sm font-medium">Confirm new password
          <input type="password" autoComplete="new-password" minLength={8} value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} className="mt-1 w-full rounded-lg border bg-background px-3 py-2.5" required />
        </label>
        <Button type="submit" disabled={busy}>{busy ? 'Saving…' : hasPassword ? 'Change password' : 'Set password'}</Button>
      </form>
      {message && <p className="mt-3 rounded-lg border bg-background/50 px-3 py-2 text-sm">{message}</p>}
    </Card>
  );
}
