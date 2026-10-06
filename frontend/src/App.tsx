import { useEffect, useMemo, useState } from 'react';
import { Database, Search, Users } from 'lucide-react';
import { JobForm } from './components/JobForm';
import { JobsPanel } from './components/JobsPanel';
import { LeadsTable } from './components/LeadsTable';
import { listJobs, listLeads, startJob } from './lib/api';
import type { Job, Lead, StartJobPayload } from './types/api';

function App() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [totalLeads, setTotalLeads] = useState(0);
  const [selectedJobId, setSelectedJobId] = useState<string | undefined>();
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refreshJobs() {
    const data = await listJobs();
    setJobs(data);
  }

  async function refreshLeads() {
    const data = await listLeads({ jobId: selectedJobId, search, limit: 100 });
    setLeads(data.items);
    setTotalLeads(data.total);
  }

  async function handleStartJob(payload: StartJobPayload) {
    setLoading(true);
    setError(null);
    try {
      const job = await startJob(payload);
      setSelectedJobId(job.id);
      await refreshJobs();
      await refreshLeads();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start job');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshJobs().catch((err) => setError(err instanceof Error ? err.message : 'Failed to load jobs'));
  }, []);

  useEffect(() => {
    refreshLeads().catch((err) => setError(err instanceof Error ? err.message : 'Failed to load leads'));
  }, [selectedJobId, search]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      refreshJobs().catch(() => undefined);
      refreshLeads().catch(() => undefined);
    }, 3000);
    return () => window.clearInterval(timer);
  }, [selectedJobId, search]);

  const stats = useMemo(() => {
    const running = jobs.filter((job) => job.status === 'running').length;
    const completed = jobs.filter((job) => job.status === 'completed').length;
    const scraped = jobs.reduce((sum, job) => sum + job.total_scraped, 0);
    return { running, completed, scraped };
  }, [jobs]);

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8 text-slate-900 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <header className="flex flex-col gap-4 rounded-3xl bg-slate-950 p-6 text-white shadow-sm md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-300">LeadGen Scraper Pro</p>
            <h1 className="mt-3 text-3xl font-bold tracking-tight md:text-4xl">Web Scraper & Lead Generation Starter Kit</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
              Dashboard siap jual untuk menjalankan job, memantau status, melihat leads, dan ekspor CSV/XLSX.
            </p>
          </div>
          <div className="rounded-2xl bg-white/10 p-4 text-sm text-slate-200 ring-1 ring-white/10">
            Backend: FastAPI · DB: PostgreSQL · Frontend: React
          </div>
        </header>

        {error ? <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}

        <section className="grid gap-4 md:grid-cols-3">
          <StatCard icon={<Search size={20} />} label="Running jobs" value={stats.running} />
          <StatCard icon={<Database size={20} />} label="Completed jobs" value={stats.completed} />
          <StatCard icon={<Users size={20} />} label="Scraped leads" value={stats.scraped} />
        </section>

        <JobForm onSubmit={handleStartJob} loading={loading} />

        <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
          <JobsPanel jobs={jobs} selectedJobId={selectedJobId} onSelectJob={setSelectedJobId} />
          <LeadsTable leads={leads} total={totalLeads} search={search} onSearchChange={setSearch} />
        </div>
      </div>
    </main>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-blue-50 p-2.5 text-blue-700">{icon}</div>
        <div>
          <p className="text-sm text-slate-500">{label}</p>
          <p className="mt-1 text-2xl font-bold text-slate-950">{value}</p>
        </div>
      </div>
    </div>
  );
}

export default App;
