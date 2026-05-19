import { AppShell } from "@/components/app-shell";
import { IncidentsTable } from "@/components/incidents-table";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { getIncidents } from "@/lib/api";
import { getNavItems } from "@/lib/navigation";

export default async function IncidentsPage() {
  const incidents = await getIncidents();

  return (
    <AppShell navItems={getNavItems("Incidents")}>
      <PageHeader
        kicker="Risk Events"
        title="Incidents"
        description="Open governance incidents created from local detection rules, reviewer escalation, and future evaluation failures."
      />

      <section className="px-5 py-5 md:px-8">
        <Panel>
          <IncidentsTable incidents={incidents} />
        </Panel>
      </section>
    </AppShell>
  );
}
