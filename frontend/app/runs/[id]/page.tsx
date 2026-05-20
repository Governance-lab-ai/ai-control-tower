import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { DetailItem, EvaluationSummaryPanel, EvidenceBlock, PiiResultCard, RetrievedDocumentsPanel, RunStepsPanel } from "@/components/run-evidence";
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
            <DetailItem label="System" value={run.ai_system_id} href={`/systems/${run.ai_system_id}`} />
            <DetailItem label="Provider" value={run.model_provider} />
            <DetailItem label="Model" value={run.model_name} />
            <DetailItem label="Version" value={run.model_version} />
            <DetailItem label="Cost" value={formatCurrencyUsd(run.cost_usd)} />
            <DetailItem label="Latency" value={formatLatency(run.latency_ms)} />
            <DetailItem label="Created" value={formatDateTime(run.created_at)} />
          </dl>
        </Panel>

        <Panel className="p-5 md:col-span-8">
          <h2 className="text-base font-semibold text-[#E6EEF8]">Evaluation</h2>
          <EvaluationSummaryPanel evaluation={run.evaluation} />

          <h2 className="mt-6 text-base font-semibold text-[#E6EEF8]">PII Flags</h2>
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            <PiiResultCard label="Input" result={run.input_pii_result} />
            <PiiResultCard label="Output" result={run.output_pii_result} />
          </div>

          <div className="mt-6 space-y-5">
            <EvidenceBlock label="Prompt" value={run.prompt} />
            <EvidenceBlock label="Input" value={run.input_text} />
            <EvidenceBlock label="Output" value={run.output_text ?? "No model output was produced for this run."} />
          </div>
        </Panel>

        <Panel className="p-5 md:col-span-12">
          <h2 className="text-base font-semibold text-[#E6EEF8]">Gateway Step Timeline</h2>
          <RunStepsPanel steps={run.run_steps} />
        </Panel>

        <Panel className="p-5 md:col-span-12">
          <h2 className="text-base font-semibold text-[#E6EEF8]">Retrieved Documents</h2>
          <RetrievedDocumentsPanel documents={run.retrieved_documents} />
        </Panel>
      </section>
    </AppShell>
  );
}
