import type { Evaluation } from "@/lib/types";

export function EvaluationBadge({ evaluation }: { evaluation: Evaluation | null }) {
  if (!evaluation) {
    return (
      <span className="inline-flex rounded-md border border-line-700 bg-panel-875 px-2 py-1 text-xs font-semibold text-[#A8B8CA]">
        Not evaluated
      </span>
    );
  }

  const className = evaluation.requires_human_review
    ? "border-amber-500/40 bg-amber-500/10 text-amber-200"
    : "border-emerald-500/40 bg-emerald-500/10 text-emerald-200";

  return <span className={`inline-flex rounded-md border px-2 py-1 text-xs font-semibold ${className}`}>{evaluation.evaluation_score}/100</span>;
}
