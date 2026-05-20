import Link from "next/link";

import type { Evaluation, PIIResult, RetrievedDocument } from "@/lib/types";

export function DetailItem({ label, value, href }: { label: string; value: string; href?: string }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">{label}</dt>
      <dd className="mt-1 break-all font-mono text-xs text-[#E6EEF8]">
        {href ? (
          <Link href={href} className="text-signal-cyan hover:text-[#E6EEF8]">
            {value}
          </Link>
        ) : (
          value
        )}
      </dd>
    </div>
  );
}

export function ScoreCard({ label, value, threshold }: { label: string; value: number; threshold?: number }) {
  return (
    <div className="rounded-lg border border-line-700 bg-navy-900 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">{label}</p>
      <p className="mt-2 font-mono text-2xl font-semibold text-[#E6EEF8]">{value}/100</p>
      {threshold !== undefined ? <p className="mt-1 text-xs text-[#A8B8CA]">Threshold {threshold}/100</p> : null}
    </div>
  );
}

export function EvaluationSummaryPanel({ evaluation }: { evaluation: Evaluation | null }) {
  if (!evaluation) {
    return <p className="mt-3 rounded-lg border border-line-700 bg-navy-900 p-4 text-sm text-[#A8B8CA]">No evaluation has been recorded for this run.</p>;
  }

  return (
    <div className="mt-3 grid gap-3 md:grid-cols-3">
      <ScoreCard label="Overall" value={evaluation.evaluation_score} threshold={evaluation.threshold} />
      <ScoreCard label="Relevance" value={evaluation.relevance_score} />
      <ScoreCard label="Groundedness" value={evaluation.groundedness_score} />
      <div className="rounded-lg border border-line-700 bg-navy-900 p-4 md:col-span-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className={evaluation.requires_human_review ? "text-xs font-semibold text-amber-200" : "text-xs font-semibold text-emerald-200"}>
            {evaluation.requires_human_review ? "Human review required" : "Evaluation passed"}
          </span>
          {evaluation.hallucination_flag ? <span className="text-xs font-semibold text-red-200">Hallucination flag</span> : null}
        </div>
        <p className="mt-3 text-sm leading-6 text-[#A8B8CA]">{evaluation.evaluation_summary}</p>
      </div>
    </div>
  );
}

export function PiiResultCard({ label, result }: { label: string; result: PIIResult }) {
  const detected = result?.pii_detected === true;
  return (
    <div className="rounded-lg border border-line-700 bg-navy-900 p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">{label}</p>
        <span className={detected ? "text-xs font-semibold text-amber-200" : "text-xs font-semibold text-emerald-200"}>
          {detected ? "PII detected" : "No PII detected"}
        </span>
      </div>
      {detected ? (
        <>
          <p className="mt-3 text-sm text-[#E6EEF8]">
            Types: {(result.pii_types ?? []).join(", ")} · Confidence: {result.confidence ?? "low"}
          </p>
          <ul className="mt-3 space-y-2 text-xs text-[#A8B8CA]">
            {(result.locations ?? []).slice(0, 3).map((location) => (
              <li key={`${location.pii_type}-${location.snippet}`} className="rounded-md border border-line-700 bg-panel-875 p-2">
                {location.snippet}
              </li>
            ))}
          </ul>
        </>
      ) : null}
    </div>
  );
}

export function SignalFlagCard({ label, active, details }: { label: string; active: boolean; details: string }) {
  return (
    <div className="rounded-lg border border-line-700 bg-navy-900 p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">{label}</p>
        <span className={active ? "text-xs font-semibold text-amber-200" : "text-xs font-semibold text-emerald-200"}>{active ? "Flagged" : "Clear"}</span>
      </div>
      <p className="mt-3 text-sm leading-6 text-[#A8B8CA]">{details || "No details recorded."}</p>
    </div>
  );
}

export function EvidenceBlock({ label, value, compact = false }: { label: string; value: string; compact?: boolean }) {
  const className = compact
    ? "mt-2 max-h-96 overflow-auto whitespace-pre-wrap rounded-lg border border-line-700 bg-navy-900 p-4 text-sm leading-6 text-[#E6EEF8]"
    : "mt-3 whitespace-pre-wrap rounded-lg border border-line-700 bg-navy-900 p-4 text-sm leading-6 text-[#E6EEF8]";

  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">{label}</p>
      <p className={className}>{value}</p>
    </div>
  );
}

export function RetrievedDocumentsPanel({ documents, dense = false }: { documents: RetrievedDocument[]; dense?: boolean }) {
  if (documents.length === 0) {
    return <p className="mt-4 text-sm text-[#A8B8CA]">No retrieved documents were attached to this run.</p>;
  }

  return (
    <div className={dense ? "mt-4 space-y-3" : "mt-4 grid gap-3 md:grid-cols-2"}>
      {documents.map((document) => (
        <div key={document.id} className="rounded-lg border border-line-700 bg-navy-900 p-4">
          <p className="font-mono text-xs uppercase tracking-[0.04em] text-[#718198]">{document.source_label}</p>
          <p className="mt-3 text-sm leading-6 text-[#E6EEF8]">{document.content}</p>
        </div>
      ))}
    </div>
  );
}
