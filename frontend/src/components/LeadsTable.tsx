import type { Lead } from '../types/api';

interface Props {
  leads: Lead[];
  total: number;
  search: string;
  onSearchChange: (value: string) => void;
}

export function LeadsTable({ leads, total, search, onSearchChange }: Props) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-900">Leads database</p>
          <p className="mt-1 text-sm text-slate-500">{total} leads ditemukan.</p>
        </div>
        <input
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Search business, phone, address..."
          className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 md:w-80"
        />
      </div>
      <div className="overflow-x-auto rounded-xl border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3 font-semibold">Business</th>
              <th className="px-4 py-3 font-semibold">Phone</th>
              <th className="px-4 py-3 font-semibold">Address</th>
              <th className="px-4 py-3 font-semibold">Rating</th>
              <th className="px-4 py-3 font-semibold">Reviews</th>
              <th className="px-4 py-3 font-semibold">Website</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {leads.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-slate-500">
                  No leads yet. Start a scraping job to populate data.
                </td>
              </tr>
            ) : (
              leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-slate-50">
                  <td className="max-w-xs px-4 py-3 font-medium text-slate-900">{lead.business_name}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600">{lead.phone_number || '-'}</td>
                  <td className="max-w-md px-4 py-3 text-slate-600">{lead.address || '-'}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600">{lead.rating ?? '-'}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600">{lead.reviews_count ?? '-'}</td>
                  <td className="max-w-xs px-4 py-3">
                    {lead.website ? (
                      <a href={lead.website} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
                        Visit
                      </a>
                    ) : (
                      <span className="text-slate-400">-</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
