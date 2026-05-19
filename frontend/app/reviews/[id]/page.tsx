import Link from "next/link";

import { IncidentSeverityBadge, IncidentStatusBadge } from "@/components/incident-badges";
import { ReviewPriorityBadge, ReviewStatusBadge } from "@/components/review-badges";
import { RunStatusBadge } from "@/components/run-status-badge";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { AppShell } from "@/components/app-shell";
import { getIncidents, getReview } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { getNavItems } from "@/lib/navigation";
import { DecisionForm } from "./decision-form";

export default async function ReviewDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [review, incidents] = await Promise.all([getReview(id), getIncidents()]);
  const runIncidents = incidents.filter((incident) => incident.model_run_id === review.model_run_id);
  const run = review.model_run;

  return (
    <AppShell navItems={getNavItems("Reviews")}>
      <PageHeader
        title={`Review ${review.id.slice(0, 8)}`}
        description="Reviewer workspace for inspecting governance evidence and recording an accountable decision."
        backLink={
          <Link href="/reviews" className="text-sm text-signal-cyan hover:text-[#E6EEF8]">
            Back to reviews
          </Link>
        }
        action={
          <div className="flex flex-wrap gap-2">
            <ReviewPriorityBadge priority={review.priority} />
            <ReviewStatusBadge status={review.status} />
          </div>
        }
      />

      <section className="grid gap-4 px-5 py-5 md:grid-cols-12 md:px-8">
        <Panel className="p-5 md:col-span-4">
          <h2 className="text-base font-semibold text-[#E6EEF8]">Review Context</h2>
          <dl className="mt-5 space-y-3">
            <Detail label="Reason" value={review.reason} />
            <Detail label="System" value={review.ai_system_id} href={`/systems/${review.ai_system_id}`} />
            <Detail label="Run" value={review.model_run_id} href={`/runs/${review.model_run_id}`} />
            <Detail label="Created" value={formatDateTime(review.created_at)} />
            {review.decided_at ? <Detail label="Decided" value={formatDateTime(review.decided_at)} /> : null}
            {review.reviewer_name ? <Detail label="Reviewer" value={review.reviewer_name} /> : null}
          </dl>
          <p className="mt-5 rounded-lg border border-line-700 bg-navy-900 p-4 text-sm leading-6 text-[#A8B8CA]">{review.summary}</p>
        </Panel>

        <Panel className="p-5 md:col-span-8">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-base font-semibold text-[#E6EEF8]">Decision</h2>
            <RunStatusBadge status={run.status} />
          </div>
          {review.decision_notes ? (
            <div className="mt-4 rounded-lg border border-line-700 bg-navy-900 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Reviewer Notes</p>
              <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-[#E6EEF8]">{review.decision_notes}</p>
            </div>
          ) : null}
          <DecisionForm reviewId={review.id} status={review.status} />
        </Panel>

        <Panel className="p-5 md:col-span-5">
          <h2 className="text-base font-semibold text-[#E6EEF8]">Risk Flags</h2>
          <div className="mt-4 grid gap-3">
            <FlagCard label="Input PII" active={run.input_pii_result?.pii_detected === true} details={(run.input_pii_result?.pii_types ?? []).join(", ")} />
            <FlagCard label="Output PII" active={run.output_pii_result?.pii_detected === true} details={(run.output_pii_result?.pii_types ?? []).join(", ")} />
            <FlagCard label="Hallucination" active={run.evaluation?.hallucination_flag === true} details={run.evaluation?.evaluation_summary ?? "No evaluation summary recorded."} />
            <FlagCard
              label="Evaluation Review"
              active={run.evaluation?.requires_human_review === true}
              details={run.evaluation ? `Score ${run.evaluation.evaluation_score}/100; threshold ${run.evaluation.threshold}/100.` : "No evaluation recorded."}
            />
          </div>
        </Panel>

        <Panel className="p-5 md:col-span-7">
          <h2 className="text-base font-semibold text-[#E6EEF8]">Evaluation Summary</h2>
          {run.evaluation ? (
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              <ScoreCard label="Overall" value={run.evaluation.evaluation_score} />
              <ScoreCard label="Relevance" value={run.evaluation.relevance_score} />
              <ScoreCard label="Groundedness" value={run.evaluation.groundedness_score} />
              <p className="rounded-lg border border-line-700 bg-navy-900 p-4 text-sm leading-6 text-[#A8B8CA] md:col-span-3">{run.evaluation.evaluation_summary}</p>
            </div>
          ) : (
            <p className="mt-4 rounded-lg border border-line-700 bg-navy-900 p-4 text-sm text-[#A8B8CA]">No evaluation has been recorded for this run.</p>
          )}
        </Panel>

        <Panel className="p-5 md:col-span-12">
          <h2 className="text-base font-semibold text-[#E6EEF8]">Run Evidence</h2>
          <div className="mt-4 grid gap-4 lg:grid-cols-3">
            <EvidenceBlock label="Prompt" value={run.prompt} />
            <EvidenceBlock label="Input" value={run.input_text} />
            <EvidenceBlock label="Output" value={run.output_text ?? "No model output was produced."} />
          </div>
        </Panel>

        <Panel className="p-5 md:col-span-7">
          <h2 className="text-base font-semibold text-[#E6EEF8]">Incidents</h2>
          {runIncidents.length > 0 ? (
            <div className="mt-4 space-y-3">
              {runIncidents.map((incident) => (
                <div key={incident.id} className="rounded-lg border border-line-700 bg-navy-900 p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="font-medium text-[#E6EEF8]">{incident.title}</p>
                      <p className="mt-1 text-xs text-[#A8B8CA]">{incident.incident_type}</p>
                    </div>
                    <div className="flex gap-2">
                      <IncidentSeverityBadge severity={incident.severity} />
                      <IncidentStatusBadge status={incident.status} />
                    </div>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-[#A8B8CA]">{incident.description}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="mt-4 text-sm text-[#A8B8CA]">No incidents are linked to this run.</p>
          )}
        </Panel>

        <Panel className="p-5 md:col-span-5">
          <h2 className="text-base font-semibold text-[#E6EEF8]">Retrieved Documents</h2>
          {run.retrieved_documents.length > 0 ? (
            <div className="mt-4 space-y-3">
              {run.retrieved_documents.map((document) => (
                <div key={document.id} className="rounded-lg border border-line-700 bg-navy-900 p-4">
                  <p className="font-mono text-xs uppercase tracking-[0.04em] text-[#718198]">{document.source_label}</p>
                  <p className="mt-3 text-sm leading-6 text-[#E6EEF8]">{document.content}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="mt-4 text-sm text-[#A8B8CA]">No retrieved documents were attached to this run.</p>
          )}
        </Panel>
      </section>
    </AppShell>
  );
}

function Detail({ label, value, href }: { label: string; value: string; href?: string }) {
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

function FlagCard({ label, active, details }: { label: string; active: boolean; details: string }) {
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

function ScoreCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-line-700 bg-navy-900 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">{label}</p>
      <p className="mt-2 font-mono text-2xl font-semibold text-[#E6EEF8]">{value}/100</p>
    </div>
  );
}

function EvidenceBlock({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">{label}</p>
      <p className="mt-2 max-h-96 overflow-auto whitespace-pre-wrap rounded-lg border border-line-700 bg-navy-900 p-4 text-sm leading-6 text-[#E6EEF8]">{value}</p>
    </div>
  );
}
