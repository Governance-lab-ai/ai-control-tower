import { AppShell } from "@/components/app-shell";
import { EvaluationsTable } from "@/components/evaluations-table";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { getEvaluations } from "@/lib/api";
import { getNavItems } from "@/lib/navigation";

export default async function EvaluationsPage() {
  const failedEvaluations = await getEvaluations(true);

  return (
    <AppShell navItems={getNavItems("Evaluations")}>
      <PageHeader
        kicker="Quality Signals"
        title="Failed Evaluations"
        description="Model runs where local evaluation scored below the configured threshold or raised a hallucination signal."
      />

      <section className="px-5 py-5 md:px-8">
        <Panel>
          <EvaluationsTable evaluations={failedEvaluations} />
        </Panel>
      </section>
    </AppShell>
  );
}
