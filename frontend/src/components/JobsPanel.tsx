import { Download } from 'lucide-react';
import { exportUrl } from '../lib/api';
import type { Job } from '../types/api';
import { StatusBadge } from './StatusBadge';

interface Props {
  jobs: Job[];
  selectedJobId?: string;
  onSelectJob: (jobId: string | undefined) => void;
}

export function JobsPanel({ jobs, selectedJobId, onSelectJob }: Props) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-slate-900">Scraping jobs</p>
          <p className="mt-1 text-sm text-slate-500">Polling otomatis setiap 3 detik.</p>
        </div>
        <button
          onClick={() => onSelectJob(undefined)}
          className="rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50"
        >
          All leads
        </button>
      </div>
      <div className="space-y-3">
        {jobs.length === 0 ? (
          <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">Belum ada job. Start job pertama dari form di atas.</p>
        ) : (
          jobs.map((job) => (
            <div
              key={job.id}
              className={`rounded-xl border p-4 transition ${
                selectedJobId === job.id ? 'border-blue-300 bg-blue-50/60' : 'border-slate-200 hover:bg-slate-50'
              }`}
            >
              <button className="w-full text-left" onClick={() => onSelectJob(job.id)}>
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="font-semibold text-slate-900">{job.keyword}</p>
                    <p className="mt-1 text-xs text-slate-500">
                      {job.location || 'No location'} · {job.target_source}
                    </p>
                  </div>
                  <StatusBadge status={job.status} />
                </div>
                <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
                  <div className="rounded-lg bg-white/80 p-3">
                    <p className="text-xs text-slate-500">Total scraped</p>
                    <p className="mt-1 font-semibold text-slate-900">{job.total_scraped}</p>
                  </div>
                  <div className="rounded-lg bg-white/80 p-3">
                    <p className="text-xs text-slate-500">Updated</p>
                    <p className="mt-1 font-semibold text-slate-900">{new Date(job.updated_at).toLocaleTimeString()}</p>
                  </div>
                </div>
                {job.error_message ? <p className="mt-3 text-xs text-rose-600">{job.error_message}</p> : null}
              </button>
              <div className="mt-3 flex gap-2">
                <a
                  href={exportUrl(job.id, 'excel')}
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-white"
                >
                  <Download size={14} /> Excel
                </a>
                <a
                  href={exportUrl(job.id, 'csv')}
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-white"
                >
                  <Download size={14} /> CSV
                </a>
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
