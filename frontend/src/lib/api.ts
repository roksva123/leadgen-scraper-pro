import type { Job, Lead, PaginatedLeads, StartJobPayload } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function listJobs(): Promise<Job[]> {
  return request<Job[]>('/jobs');
}

export function startJob(payload: StartJobPayload): Promise<Job> {
  return request<Job>('/jobs/start', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listLeads(params: { jobId?: string; search?: string; limit?: number; offset?: number }): Promise<PaginatedLeads> {
  const query = new URLSearchParams();
  if (params.jobId) query.set('job_id', params.jobId);
  if (params.search) query.set('search', params.search);
  query.set('limit', String(params.limit ?? 50));
  query.set('offset', String(params.offset ?? 0));
  return request<PaginatedLeads>(`/leads?${query.toString()}`);
}

export function exportUrl(jobId: string, format: 'excel' | 'csv'): string {
  return `${API_BASE_URL}/export/${jobId}?format=${format}`;
}

export function countLeadsByJob(leads: Lead[]): Record<string, number> {
  return leads.reduce<Record<string, number>>((acc, lead) => {
    acc[lead.job_id] = (acc[lead.job_id] ?? 0) + 1;
    return acc;
  }, {});
}
