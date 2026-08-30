import type { HealthStatus, User } from '@/types';

function resolveApiBaseUrl(): string {
  const configured = (process.env.NEXT_PUBLIC_API_URL || '').trim().replace(/\/$/, '');
  if (typeof window === 'undefined') {
    return configured || 'http://localhost:8000';
  }

  // A browser opened at http://<laptop-ip>:3000 cannot reach the laptop's
  // backend through the browser's own localhost. When no explicit API host
  // is configured, use the same hostname with the backend port.
  if (!configured || configured === 'http://localhost:8000' || configured === 'http://127.0.0.1:8000') {
    return `${window.location.protocol}//${window.location.hostname}:8000`;
  }
  return configured;
}

class ApiClient {
  private token(): string | null {
    if (typeof window === 'undefined') return null;
    const accessToken = localStorage.getItem('access_token');
    const legacyToken = localStorage.getItem('careeros_token');
    return accessToken || legacyToken;
  }

  hasToken(): boolean { return !!this.token(); }

  clearToken(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('access_token');
    localStorage.removeItem('careeros_token');
    localStorage.removeItem('user');
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers);
    if (!headers.has('Content-Type') && options.body) headers.set('Content-Type', 'application/json');
    const token = this.token();
    if (token) headers.set('Authorization', `Bearer ${token}`);

    const response = await fetch(`${resolveApiBaseUrl()}${endpoint}`, {
      ...options,
      headers,
      cache: 'no-store',
    });
    const text = await response.text();
    let data: any = null;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }
    if (!response.ok) {
      if (response.status === 401) this.clearToken();
      throw new Error(data?.detail || data?.message || `API ${response.status}`);
    }
    return data as T;
  }

  get<T>(endpoint: string) { return this.request<T>(endpoint); }
  post<T>(endpoint: string, body: any) { return this.request<T>(endpoint, { method: 'POST', body: JSON.stringify(body) }); }
  patch<T>(endpoint: string, body: any) { return this.request<T>(endpoint, { method: 'PATCH', body: JSON.stringify(body) }); }
  put<T>(endpoint: string, body: any) { return this.request<T>(endpoint, { method: 'PUT', body: JSON.stringify(body) }); }
  delete<T>(endpoint: string) { return this.request<T>(endpoint, { method: 'DELETE' }); }

  healthCheck() { return this.get<HealthStatus>('/api/v1/health'); }
  ping() { return this.get<{ timestamp: string; message: string }>('/api/v1/ping'); }
  me() { return this.get<User>('/api/v1/auth/me'); }
  register(body: any) { return this.post<any>('/api/v1/auth/register', body); }
  login(body: any) { return this.post<any>('/api/v1/auth/login', body); }

  profile() { return this.get<any>('/api/v1/career/profile'); }
  saveProfile(body: any) { return this.post<any>('/api/v1/career/profile', body); }
  evidence() { return this.get<any[]>('/api/v1/career/evidence'); }
  addEvidence(body: any) { return this.post<any>('/api/v1/career/evidence', body); }

  personas(userId: string) { return this.get<any[]>(`/api/v1/personas/?user_id=${encodeURIComponent(userId)}`); }
  createPersona(body: any) { return this.post<any>('/api/v1/personas/', body); }
  updatePersona(id: string, body: any) { return this.put<any>(`/api/v1/personas/${id}`, body); }
  activatePersona(id: string) { return this.post<any>(`/api/v1/personas/${id}/activate`, {}); }

  jobs(userId: string) { return this.get<any[]>(`/api/v1/jobs/?user_id=${encodeURIComponent(userId)}`); }
  analyzeJob(body: any) { return this.post<any>('/api/v1/jobs/analyze', body); }
  jobDna(id: string) { return this.get<any>(`/api/v1/jobs/${id}/dna`); }

  applications() { return this.get<any[]>('/api/v1/applications'); }
  createApplication(body: any) { return this.post<any>('/api/v1/applications', body); }
  updateApplicationStatus(id: string, status: string) { return this.patch<any>(`/api/v1/applications/${id}/status?status_value=${encodeURIComponent(status)}`, {}); }
  applicationPackage(id: string) { return this.post<any>(`/api/v1/applications/${id}/package`, {}); }
  truthCheck(id: string) { return this.post<any>(`/api/v1/truth/${id}`, {}); }

  companies() { return this.get<any[]>('/api/v1/companies/intelligence'); }
  saveCompany(body: any) { return this.post<any>('/api/v1/companies/intelligence', body); }

  interviews() { return this.get<any[]>('/api/v1/interviews'); }
  createInterview(body: any) { return this.post<any>('/api/v1/interviews', body); }
  startLive(body: any) { return this.post<any>('/api/v1/live-interview/sessions', body); }
  assistLive(id: string, question: string) { return this.post<any>(`/api/v1/live-interview/sessions/${id}/assist`, { question }); }

  analytics() { return this.get<any>('/api/v1/analytics/summary'); }
}

export const apiClient = new ApiClient();
export { resolveApiBaseUrl };