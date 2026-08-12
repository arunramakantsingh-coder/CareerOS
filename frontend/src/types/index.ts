export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  database?: string;
  version: string;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
  locale: string;
  timezone: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Tenant {
  id: string;
  name: string;
  plan: string;
  status: string;
  settings?: string;
  created_at: string;
  updated_at: string;
}