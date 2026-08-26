import type { HealthStatus } from '@/types';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

class ApiClient {
  private token() { return typeof window !== 'undefined' ? localStorage.getItem('careeros_token') : null; }
  clearToken() { if (typeof window !== 'undefined') localStorage.removeItem('careeros_token'); }
  hasToken() { return !!this.token(); }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers);
    if (!headers.has('Content-Type') && options.body) headers.set('Content-Type', 'application/json');
    const token = this.token();
    if (token) headers.set('Authorization', `Bearer ${token}`);
    const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers, cache: 'no-store' });
    const text = await response.text();
    let data: any = null;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }
    if (!response.ok) {
      if (response.status === 401 && typeof window !== 'undefined') localStorage.removeItem('careeros_token');
      throw new Error(data?.detail || data?.message || `API ${response.status}`);
    }
    return data as T;
  }
  get<T>(endpoint:string){ return this.request<T>(endpoint); }
  post<T>(endpoint:string, body:any){ return this.request<T>(endpoint,{method:'POST',body:JSON.stringify(body)}); }
  patch<T>(endpoint:string, body:any){ return this.request<T>(endpoint,{method:'PATCH',body:JSON.stringify(body)}); }
  put<T>(endpoint:string, body:any){ return this.request<T>(endpoint,{method:'PUT',body:JSON.stringify(body)}); }
  delete<T>(endpoint:string){ return this.request<T>(endpoint,{method:'DELETE'}); }

  healthCheck(){ return this.get<HealthStatus>('/api/v1/health'); }
  me(){ return this.get<any>('/api/v1/auth/me'); }
  register(body:any){ return this.post<any>('/api/v1/auth/register',body); }
  login(body:any){ return this.post<any>('/api/v1/auth/login',body); }
  profile(){ return this.get<any>('/api/v1/career/profile'); }
  saveProfile(body:any){ return this.post<any>('/api/v1/career/profile',body); }
  evidence(){ return this.get<any[]>('/api/v1/career/evidence'); }
  addEvidence(body:any){ return this.post<any>('/api/v1/career/evidence',body); }
  personas(userId:string){ return this.get<any[]>(`/api/v1/personas/?user_id=${encodeURIComponent(userId)}`); }
  createPersona(body:any){ return this.post<any>('/api/v1/personas/',body); }
  updatePersona(id:string,body:any){ return this.put<any>(`/api/v1/personas/${id}`,body); }
  activatePersona(id:string){ return this.post<any>(`/api/v1/personas/${id}/activate`,{}); }
  jobs(userId:string){ return this.get<any[]>(`/api/v1/jobs/?user_id=${encodeURIComponent(userId)}`); }
  analyzeJob(body:any){ return this.post<any>('/api/v1/jobs/analyze',body); }
  jobDna(id:string){ return this.get<any>(`/api/v1/jobs/${id}/dna`); }
  applications(){ return this.get<any[]>('/api/v1/applications'); }
  createApplication(body:any){ return this.post<any>('/api/v1/applications',body); }
  updateApplicationStatus(id:string,status:string){ return this.patch<any>(`/api/v1/applications/${id}/status?status_value=${encodeURIComponent(status)}`,{}); }
  applicationPackage(id:string){ return this.post<any>(`/api/v1/applications/${id}/package`,{}); }
  truthCheck(id:string){ return this.post<any>(`/api/v1/truth/${id}`,{}); }
  companies(){ return this.get<any[]>('/api/v1/companies/intelligence'); }
  saveCompany(body:any){ return this.post<any>('/api/v1/companies/intelligence',body); }
  interviews(){ return this.get<any[]>('/api/v1/interviews'); }
  createInterview(body:any){ return this.post<any>('/api/v1/interviews',body); }
  startLive(body:any){ return this.post<any>('/api/v1/live-interview/sessions',body); }
  assistLive(id:string,question:string){ return this.post<any>(`/api/v1/live-interview/sessions/${id}/assist`,{question}); }
  analytics(){ return this.get<any>('/api/v1/analytics/summary'); }
}
export const apiClient = new ApiClient();
