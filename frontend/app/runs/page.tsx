import { AppShell } from "@/components/app-shell";
import { ModelRunsTable } from "@/components/model-runs-table";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { getModelRuns } from "@/lib/api";
import { getNavItems } from "@/lib/navigation";

export default async function RunsPage() {
  const runs = await getModelRuns();

  return (
    <AppShell navItems={getNavItems("Runs")}>
      <PageHeader
        kicker="Evidence"
        title="Model Runs"
        description="Persistent gateway execution records with prompts, inputs, outputs, provider metadata, cost, latency, and retrieval evidence."
      />

      <section className="px-5 py-5 md:px-8">
        <Panel>
          <ModelRunsTable runs={runs} showSystem />
        </Panel>
      </section>
    </AppShell>
  );
}
