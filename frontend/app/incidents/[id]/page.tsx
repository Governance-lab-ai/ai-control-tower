import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { IncidentSeverityBadge, IncidentStatusBadge } from "@/components/incident-badges";
import { DetailItem } from "@/components/run-evidence";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { getIncident } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { getNavItems } from "@/lib/navigation";
import { IncidentStatusForm } from "./incident-status-form";

export default async function IncidentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const incident = await getIncident(id);

  return (
    <AppShell navItems={getNavItems("Incidents")}>
      <PageHeader
        title={`Incident ${incident.id.slice(0, 8)}`}
        description="Risk event record linked to governed runs, systems, and reviewer follow-up."
        backLink={
          <Link href="/incidents" className="text-sm text-signal-cyan hover:text-[#E6EEF8]">
            Back to incidents
          </Link>
        }
        action={
          <div className="flex flex-wrap gap-2">
            <IncidentSeverityBadge severity={incident.severity} />
            <IncidentStatusBadge status={incident.status} />
          </div>
        }
      />

      <section className="grid gap-4 px-5 py-5 md:grid-cols-12 md:px-8">
        <Panel className="p-5 md:col-span-5">
          <h2 className="text-base font-semibold text-[#E6EEF8]">Incident Metadata</h2>
          <dl className="mt-5 space-y-3">
            <DetailItem label="Type" value={incident.incident_type} />
            <DetailItem label="System" value={incident.ai_system_id} href={`/systems/${incident.ai_system_id}`} />
            {incident.model_run_id ? <DetailItem label="Run" value={incident.model_run_id} href={`/runs/${incident.model_run_id}`} /> : null}
            <DetailItem label="Created" value={formatDateTime(incident.created_at)} />
            <DetailItem label="Updated" value={formatDateTime(incident.updated_at)} />
          </dl>
        </Panel>

        <Panel className="p-5 md:col-span-7">
          <h2 className="text-base font-semibold text-[#E6EEF8]">{incident.title}</h2>
          <p className="mt-4 whitespace-pre-wrap rounded-lg border border-line-700 bg-navy-900 p-4 text-sm leading-6 text-[#A8B8CA]">{incident.description}</p>
          <IncidentStatusForm incidentId={incident.id} status={incident.status} />
        </Panel>
      </section>
    </AppShell>
  );
}
