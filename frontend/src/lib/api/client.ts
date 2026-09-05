import type { HealthStatus, User } from '@/types';

function resolveApiBaseUrl(): string {
  const configured = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/$/, '');
  if (typeof window === 'undefined') return configured || 'http://localhost:8000';
  if (!configured || configured === 'http://localhost:8000' || configured === 'http://127.0.0.1:8000') return `${window.location.protocol}//${window.location.hostname}:8000`;
  return configured;
}

function apiErrorMessage(data: any, fallback: string): string {
  const detail = data?.detail ?? data?.message ?? data?.error;
  if (typeof detail === 'string' && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const messages = detail.map(item => typeof item === 'string' ? item : item?.msg || item?.message || 'Validation error').filter(Boolean);
    if (messages.length) return messages.join(' • ');
  }
  if (detail && typeof detail === 'object') {
    if (typeof detail.msg === 'string') return detail.msg;
    if (typeof detail.message === 'string') return detail.message;
    try { return JSON.stringify(detail); } catch { return fallback; }
  }
  return fallback;
}

class ApiClient {
  private token(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token') || localStorage.getItem('careeros_token');
  }
  hasToken(): boolean { return !!this.token(); }
  clearToken(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('access_token'); localStorage.removeItem('careeros_token'); localStorage.removeItem('user');
  }
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers);
    if (!headers.has('Content-Type') && options.body) headers.set('Content-Type', 'application/json');
    const token = this.token(); if (token) headers.set('Authorization', `Bearer ${token}`);
    let response: Response;
    try { response = await fetch(`${resolveApiBaseUrl()}${endpoint}`, { ...options, headers, cache: 'no-store' }); }
    catch { throw new Error(`Unable to reach CareerOS API at ${resolveApiBaseUrl()}. Check that the backend is running and reachable from this device.`); }
    const text = await response.text(); let data: any = null;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }
    if (!response.ok) { if (response.status === 401) this.clearToken(); throw new Error(apiErrorMessage(data, `API ${response.status}`)); }
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

  identityOverview() { return this.get<any>('/api/v1/identity/overview'); }
  evidenceLibrary(params = '') { return this.get<any>(`/api/v1/identity/evidence-library${params ? `?${params}` : ''}`); }
  documentDetail(id: string) { return this.get<any>(`/api/v1/identity/documents/${id}`); }
  documentContent(id: string) { return this.request<Blob>(`/api/v1/identity/documents/${id}/content`, { headers: { Accept: '*/*' } }).then(async () => { throw new Error('Use openDocumentContent for binary content'); }); }
  async openDocumentContent(id: string): Promise<Blob> {
    const token = this.token();
    const response = await fetch(`${resolveApiBaseUrl()}/api/v1/identity/documents/${id}/content`, { headers: token ? { Authorization: `Bearer ${token}` } : {}, cache: 'no-store' });
    if (!response.ok) throw new Error(`Unable to open document (HTTP ${response.status})`);
    return response.blob();
  }
  reclassifyDocument(id: string) { return this.post<any>(`/api/v1/identity/documents/${id}/reclassify`, {}); }
  generatePersonaSuggestions() { return this.post<any[]>('/api/v1/identity/personas/suggestions/generate', {}); }
  personaSuggestions() { return this.get<any[]>('/api/v1/identity/personas/suggestions'); }
  activatePersonaSuggestion(id: string) { return this.post<any>(`/api/v1/identity/personas/suggestions/${id}/activate`, {}); }
  connectionDiagnostics() { return this.get<any>('/api/v1/identity/connections/diagnostics'); }

  personas(userId: string) { return this.get<any[]>(`/api/v1/personas/?user_id=${encodeURIComponent(userId)}`); }
  createPersona(body: any) { return this.post<any>('/api/v1/personas/', body); }
  updatePersona(id: string, body: any) { return this.put<any>(`/api/v1/personas/${id}`, body); }
  activatePersona(id: string) { return this.post<any>(`/api/v1/personas/${id}/activate`, {}); }
  deletePersona(id: string) { return this.delete<any>(`/api/v1/personas/${id}`); }

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