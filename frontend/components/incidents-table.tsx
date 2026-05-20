import Link from "next/link";

import { IncidentSeverityBadge, IncidentStatusBadge } from "@/components/incident-badges";
import { formatDateTime } from "@/lib/format";
import type { Incident } from "@/lib/types";

export function IncidentsTable({ incidents }: { incidents: Incident[] }) {
  if (incidents.length === 0) {
    return <p className="p-5 text-sm text-[#A8B8CA]">No incidents recorded.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-navy-900/70 text-xs uppercase tracking-[0.04em] text-[#718198]">
          <tr>
            <th className="px-5 py-3 font-semibold">Incident</th>
            <th className="px-5 py-3 font-semibold">Type</th>
            <th className="px-5 py-3 font-semibold">Severity</th>
            <th className="px-5 py-3 font-semibold">Status</th>
            <th className="px-5 py-3 font-semibold">Run</th>
            <th className="px-5 py-3 font-semibold">Created</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line-700">
          {incidents.map((incident) => (
            <tr key={incident.id} className="hover:bg-panel-825/60">
              <td className="px-5 py-4">
                <Link href={`/incidents/${incident.id}`} className="font-medium text-[#E6EEF8] hover:text-signal-cyan">
                  {incident.title}
                </Link>
                <p className="mt-1 max-w-xl truncate text-xs text-[#A8B8CA]">{incident.description}</p>
              </td>
              <td className="px-5 py-4 font-mono text-xs text-[#A8B8CA]">{incident.incident_type}</td>
              <td className="px-5 py-4">
                <IncidentSeverityBadge severity={incident.severity} />
              </td>
              <td className="px-5 py-4">
                <IncidentStatusBadge status={incident.status} />
              </td>
              <td className="px-5 py-4">
                {incident.model_run_id ? (
                  <Link href={`/runs/${incident.model_run_id}`} className="font-mono text-xs text-signal-cyan hover:text-[#E6EEF8]">
                    {incident.model_run_id.slice(0, 8)}
                  </Link>
                ) : (
                  <span className="text-xs text-[#718198]">None</span>
                )}
              </td>
              <td className="px-5 py-4 text-[#A8B8CA]">{formatDateTime(incident.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
