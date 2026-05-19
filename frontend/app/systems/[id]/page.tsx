import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { ApprovalBadge, RiskBadge } from "@/components/registry-badges";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { getSystem } from "@/lib/api";
import { formatBooleanYesNo, formatDateTime, formatRequired } from "@/lib/format";
import { getNavItems } from "@/lib/navigation";
import { ApprovalStatusControl } from "./approval-status-control";
import { TestRunPanel } from "./components/test-run-panel";

export default async function SystemDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const system = await getSystem(id);

  return (
    <AppShell navItems={getNavItems("AI Systems")}>
      <PageHeader
        title={system.name}
        description={system.description}
        backLink={
          <Link href="/systems" className="text-sm text-signal-cyan hover:text-[#E6EEF8]">
            Back to registry
          </Link>
        }
        action={
          <div className="flex gap-2">
            <RiskBadge level={system.risk_level} />
            <ApprovalBadge status={system.approval_status} />
          </div>
        }
      />

      <section className="grid gap-4 px-5 py-5 md:grid-cols-12 md:px-8">
        <Panel className="p-5 md:col-span-8">
          <h2 className="text-base font-semibold text-[#E6EEF8]">System Passport</h2>
          <dl className="mt-5 grid gap-4 md:grid-cols-2">
            <Detail label="Department" value={system.department} />
            <Detail label="Owner" value={`${system.owner_name} (${system.owner_email})`} />
            <Detail label="Model provider" value={system.model_provider} />
            <Detail label="Model name" value={system.model_name} />
            <Detail label="Personal data" value={formatBooleanYesNo(system.contains_personal_data)} />
            <Detail label="Human oversight" value={formatRequired(system.human_oversight_required)} />
            <Detail label="Created" value={formatDateTime(system.created_at)} />
            <Detail label="Updated" value={formatDateTime(system.updated_at)} />
          </dl>
        </Panel>

        <aside className="space-y-4 md:col-span-4">
          <ApprovalStatusControl systemId={system.id} currentStatus={system.approval_status} />
          <Panel className="p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Data sources</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {system.data_sources.length > 0 ? (
                system.data_sources.map((source) => (
                  <span key={source} className="rounded-md border border-line-700 bg-navy-900 px-2 py-1 font-mono text-xs text-[#A8B8CA]">
                    {source}
                  </span>
                ))
              ) : (
                <span className="text-sm text-[#A8B8CA]">No data sources recorded.</span>
              )}
            </div>
          </Panel>
        </aside>
        <TestRunPanel systemId={system.id} approvalStatus={system.approval_status} />
      </section>
    </AppShell>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-line-700 bg-navy-900 p-3">
      <dt className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">{label}</dt>
      <dd className="mt-2 text-sm text-[#E6EEF8]">{value}</dd>
    </div>
  );
}
