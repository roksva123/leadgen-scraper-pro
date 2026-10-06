export type JobStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface Job {
  id: string;
  keyword: string;
  location: string | null;
  target_source: string;
  status: JobStatus;
  total_scraped: number;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface Lead {
  id: string;
  job_id: string;
  business_name: string;
  phone_number: string | null;
  address: string | null;
  rating: number | null;
  reviews_count: number | null;
  website: string | null;
  extra_metadata: Record<string, unknown>;
  created_at: string;
}

export interface PaginatedLeads {
  items: Lead[];
  total: number;
  limit: number;
  offset: number;
}

export interface StartJobPayload {
  keyword: string;
  location?: string;
  target_source: string;
  max_results: number;
}
