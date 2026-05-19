import Link from "next/link";

import { EvaluationBadge } from "@/components/evaluation-badge";
import { RunStatusBadge } from "@/components/run-status-badge";
import { formatCurrencyUsd, formatDateTime, formatLatency } from "@/lib/format";
import type { ModelRun } from "@/lib/types";

export function ModelRunsTable({
  runs,
  showSystem = false,
}: {
  runs: ModelRun[];
  showSystem?: boolean;
}) {
  if (runs.length === 0) {
    return <p className="p-5 text-sm text-[#A8B8CA]">No model runs recorded yet.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-navy-900/70 text-xs uppercase tracking-[0.04em] text-[#718198]">
          <tr>
            <th className="px-5 py-3 font-semibold">Run</th>
            {showSystem ? <th className="px-5 py-3 font-semibold">System</th> : null}
            <th className="px-5 py-3 font-semibold">Model</th>
            <th className="px-5 py-3 font-semibold">Cost</th>
            <th className="px-5 py-3 font-semibold">Latency</th>
            <th className="px-5 py-3 font-semibold">Evaluation</th>
            <th className="px-5 py-3 font-semibold">Status</th>
            <th className="px-5 py-3 font-semibold">Created</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line-700">
          {runs.map((run) => (
            <tr key={run.id} className="hover:bg-panel-825/60">
              <td className="px-5 py-4">
                <Link href={`/runs/${run.id}`} className="font-mono text-xs text-signal-cyan hover:text-[#E6EEF8]">
                  {run.id.slice(0, 8)}
                </Link>
                <p className="mt-1 max-w-sm truncate text-xs text-[#A8B8CA]">{run.input_text}</p>
              </td>
              {showSystem ? (
                <td className="px-5 py-4">
                  <Link href={`/systems/${run.ai_system_id}`} className="font-mono text-xs text-signal-cyan hover:text-[#E6EEF8]">
                    {run.ai_system_id.slice(0, 8)}
                  </Link>
                </td>
              ) : null}
              <td className="px-5 py-4">
                <p className="text-[#E6EEF8]">{run.model_name}</p>
                <p className="font-mono text-xs text-[#A8B8CA]">{run.model_provider}</p>
              </td>
              <td className="px-5 py-4 font-mono text-xs text-[#E6EEF8]">{formatCurrencyUsd(run.cost_usd)}</td>
              <td className="px-5 py-4 font-mono text-xs text-[#E6EEF8]">{formatLatency(run.latency_ms)}</td>
              <td className="px-5 py-4">
                <EvaluationBadge evaluation={run.evaluation} />
              </td>
              <td className="px-5 py-4">
                <RunStatusBadge status={run.status} />
              </td>
              <td className="px-5 py-4 text-[#A8B8CA]">{formatDateTime(run.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
