import Link from "next/link";

import { formatDateTime } from "@/lib/format";
import type { Evaluation } from "@/lib/types";

export function EvaluationsTable({ evaluations }: { evaluations: Evaluation[] }) {
  if (evaluations.length === 0) {
    return <p className="p-5 text-sm text-[#A8B8CA]">No failed evaluations recorded.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-navy-900/70 text-xs uppercase tracking-[0.04em] text-[#718198]">
          <tr>
            <th className="px-5 py-3 font-semibold">Run</th>
            <th className="px-5 py-3 font-semibold">Score</th>
            <th className="px-5 py-3 font-semibold">Relevance</th>
            <th className="px-5 py-3 font-semibold">Groundedness</th>
            <th className="px-5 py-3 font-semibold">Signal</th>
            <th className="px-5 py-3 font-semibold">Created</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line-700">
          {evaluations.map((evaluation) => (
            <tr key={evaluation.id} className="hover:bg-panel-825/60">
              <td className="px-5 py-4">
                <Link href={`/runs/${evaluation.model_run_id}`} className="font-mono text-xs text-signal-cyan hover:text-[#E6EEF8]">
                  {evaluation.model_run_id.slice(0, 8)}
                </Link>
                <p className="mt-1 font-mono text-xs text-[#718198]">{evaluation.provider}</p>
              </td>
              <td className="px-5 py-4 font-mono text-xs text-[#E6EEF8]">
                {evaluation.evaluation_score}/100
                <p className="mt-1 text-[#718198]">threshold {evaluation.threshold}</p>
              </td>
              <td className="px-5 py-4 font-mono text-xs text-[#E6EEF8]">{evaluation.relevance_score}/100</td>
              <td className="px-5 py-4 font-mono text-xs text-[#E6EEF8]">{evaluation.groundedness_score}/100</td>
              <td className="px-5 py-4">
                <span className={evaluation.hallucination_flag ? "text-xs font-semibold text-red-200" : "text-xs font-semibold text-amber-200"}>
                  {evaluation.hallucination_flag ? "Hallucination flag" : "Below threshold"}
                </span>
                <p className="mt-1 max-w-md text-xs leading-5 text-[#A8B8CA]">{evaluation.evaluation_summary}</p>
              </td>
              <td className="px-5 py-4 text-[#A8B8CA]">{formatDateTime(evaluation.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
