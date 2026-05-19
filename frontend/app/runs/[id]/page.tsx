import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { RunStatusBadge } from "@/components/run-status-badge";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { getModelRun } from "@/lib/api";
import { formatCurrencyUsd, formatDateTime, formatLatency } from "@/lib/format";
import { getNavItems } from "@/lib/navigation";

export default async function RunDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const run = await getModelRun(id);

  return (
    <AppShell navItems={getNavItems("Runs")}>
      <PageHeader
        title={`Run ${run.id.slice(0, 8)}`}
        description="Audit evidence captured by the governance gateway for a single executed model run."
        backLink={
          <Link href="/runs" className="text-sm text-signal-cyan hover:text-[#E6EEF8]">
            Back to runs
          </Link>
        }
        action={<RunStatusBadge status={run.status} />}
      />

      <section className="grid gap-4 px-5 py-5 md:grid-cols-12 md:px-8">
        <Panel className="p-5 md:col-span-4">
          <h2 className="text-base font-semibold text-[#E6EEF8]">Execution Metadata</h2>
          <dl className="mt-5 space-y-3">
            <Detail label="System" value={run.ai_system_id} href={`/systems/${run.ai_system_id}`} />
            <Detail label="Provider" value={run.model_provider} />
            <Detail label="Model" value={run.model_name} />
            <Detail label="Version" value={run.model_version} />
            <Detail label="Cost" value={formatCurrencyUsd(run.cost_usd)} />
            <Detail label="Latency" value={formatLatency(run.latency_ms)} />
            <Detail label="Created" value={formatDateTime(run.created_at)} />
          </dl>
        </Panel>

        <Panel className="p-5 md:col-span-8">
          <h2 className="text-base font-semibold text-[#E6EEF8]">PII Flags</h2>
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            <PiiResultCard label="Input" result={run.input_pii_result} />
            <PiiResultCard label="Output" result={run.output_pii_result} />
          </div>

          <h2 className="mt-6 text-base font-semibold text-[#E6EEF8]">Prompt</h2>
          <EvidenceText value={run.prompt} />
          <h2 className="mt-6 text-base font-semibold text-[#E6EEF8]">Input</h2>
          <EvidenceText value={run.input_text} />
          <h2 className="mt-6 text-base font-semibold text-[#E6EEF8]">Output</h2>
          <EvidenceText value={run.output_text ?? "No model output was produced for this run."} />
        </Panel>

        <Panel className="p-5 md:col-span-12">
          <h2 className="text-base font-semibold text-[#E6EEF8]">Retrieved Documents</h2>
          {run.retrieved_documents.length > 0 ? (
            <div className="mt-4 grid gap-3 md:grid-cols-2">
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

function EvidenceText({ value }: { value: string }) {
  return <p className="mt-3 whitespace-pre-wrap rounded-lg border border-line-700 bg-navy-900 p-4 text-sm leading-6 text-[#E6EEF8]">{value}</p>;
}

function PiiResultCard({
  label,
  result,
}: {
  label: string;
  result: {
    pii_detected?: boolean;
    pii_types?: string[];
    confidence?: string;
    locations?: Array<{ snippet: string; pii_type: string }>;
  };
}) {
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
