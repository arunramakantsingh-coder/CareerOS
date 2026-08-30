import type { HealthStatus, User } from '@/types';

function resolveApiBaseUrl() {
  const configured = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (configured) return configured.replace(/\/$/, '');
  if (typeof window !== 'undefined') return `${window.location.protocol}//${window.location.hostname}:8000`;
  return 'http://localhost:8000';
}
const API_BASE_URL = resolveApiBaseUrl();

class ApiClient {
  private token(): string | null { if (typeof window === 'undefined') return null; return localStorage.getItem('access_token') || localStorage.getItem('careeros_token'); }
  hasToken() { return !!this.token(); }
  clearToken() { if (typeof window === 'undefined') return; localStorage.removeItem('access_token'); localStorage.removeItem('careeros_token'); localStorage.removeItem('user'); }
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers);
    if (!headers.has('Content-Type') && options.body && !(options.body instanceof FormData)) headers.set('Content-Type', 'application/json');
    const token = this.token(); if (token) headers.set('Authorization', `Bearer ${token}`);
    const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers, cache: 'no-store' });
    const text = await response.text(); let data: any = null; try { data = text ? JSON.parse(text) : null; } catch { data = text; }
    if (!response.ok) { if (response.status === 401) this.clearToken(); throw new Error(data?.detail || data?.message || `API ${response.status}`); }
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
  candidateProfile() { return this.get<any>('/api/v1/profile/'); }
  createCandidateProfile(body: any) { return this.post<any>('/api/v1/profile/', body); }
  updateCandidateProfile(body: any) { return this.put<any>('/api/v1/profile/', body); }
  profileCompleteness() { return this.get<any>('/api/v1/profile/completeness'); }
  experiences() { return this.get<any[]>('/api/v1/profile/experiences'); }
  skills() { return this.get<any[]>('/api/v1/profile/skills'); }
  certifications() { return this.get<any[]>('/api/v1/profile/certifications'); }
  educations() { return this.get<any[]>('/api/v1/profile/educations'); }
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
  documents() { return this.get<any[]>('/api/v1/documents/'); }
  extractionSummary() { return this.get<any>('/api/v1/extraction/summary'); }
  extractedProfile() { return this.get<any>('/api/v1/extraction/profile'); }
  extractionResults() { return this.get<any[]>('/api/v1/extraction/results'); }

  async uploadDocuments(files: File[], options: { category?: string; subcategory?: string; onProgress?: (index: number, progress: number) => void } = {}) {
    const results: any[] = [];
    for (let index = 0; index < files.length; index += 1) {
      const file = files[index]; const formData = new FormData(); formData.append('file', file);
      if (options.category) formData.append('document_category', options.category); if (options.subcategory) formData.append('document_subcategory', options.subcategory);
      results.push(await this.request<any>('/api/v1/documents/upload', { method: 'POST', body: formData })); options.onProgress?.(index, 100);
    }
    return results;
  }
  async uploadBulk(files: File[], options: { category?: string; subcategory?: string; onProgress?: (progress: number) => void } = {}) {
    const formData = new FormData(); files.forEach((file) => formData.append('files', file, file.webkitRelativePath || file.name));
    if (options.category) formData.append('document_category', options.category); if (options.subcategory) formData.append('document_subcategory', options.subcategory);
    options.onProgress?.(10);
    const result = await this.request<any>('/api/v1/documents/bulk-upload', { method: 'POST', body: formData });
    options.onProgress?.(95);
    return result;
  }
}
export const apiClient = new ApiClient();
