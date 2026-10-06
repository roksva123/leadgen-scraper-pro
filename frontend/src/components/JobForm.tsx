import { FormEvent, useState } from 'react';
import { Play } from 'lucide-react';
import type { StartJobPayload } from '../types/api';

interface Props {
  onSubmit: (payload: StartJobPayload) => Promise<void>;
  loading: boolean;
}

export function JobForm({ onSubmit, loading }: Props) {
  const [keyword, setKeyword] = useState('Restoran');
  const [location, setLocation] = useState('Jakarta');
  const [targetSource, setTargetSource] = useState('demo_directory');
  const [maxResults, setMaxResults] = useState(25);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await onSubmit({
      keyword,
      location,
      target_source: targetSource,
      max_results: maxResults,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-5">
        <p className="text-sm font-semibold text-slate-900">Start scraping job</p>
        <p className="mt-1 text-sm text-slate-500">Gunakan demo source untuk sample data, atau Google Places API jika API key sudah diset.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-4">
        <label className="space-y-1.5 md:col-span-1">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">Keyword</span>
          <input
            value={keyword}
            onChange={(event) => setKeyword(event.target.value)}
            className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            placeholder="Restoran"
            required
            minLength={2}
          />
        </label>
        <label className="space-y-1.5 md:col-span-1">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">Location</span>
          <input
            value={location}
            onChange={(event) => setLocation(event.target.value)}
            className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            placeholder="Jakarta"
          />
        </label>
        <label className="space-y-1.5">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">Source</span>
          <select
            value={targetSource}
            onChange={(event) => setTargetSource(event.target.value)}
            className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
          >
            <option value="demo_directory">Demo Directory</option>
            <option value="google_places">Google Places API</option>
          </select>
        </label>
        <label className="space-y-1.5">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">Max Results</span>
          <input
            type="number"
            min={1}
            max={200}
            value={maxResults}
            onChange={(event) => setMaxResults(Number(event.target.value))}
            className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
          />
        </label>
      </div>
      <button
        type="submit"
        disabled={loading}
        className="mt-5 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        <Play size={16} />
        {loading ? 'Starting...' : 'Start Job'}
      </button>
    </form>
  );
}
