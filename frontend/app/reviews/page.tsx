import { AppShell } from "@/components/app-shell";
import { ReviewsTable } from "@/components/reviews-table";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { getReviews } from "@/lib/api";
import { getNavItems } from "@/lib/navigation";

export default async function ReviewsPage() {
  const reviews = await getReviews("pending");

  return (
    <AppShell navItems={getNavItems("Reviews")}>
      <PageHeader
        kicker="Human Oversight"
        title="Review Queue"
        description="Pending reviewer decisions for risky model runs, PII flags, hallucination signals, failed evaluations, and high-risk systems."
      />

      <section className="px-5 py-5 md:px-8">
        <Panel>
          <ReviewsTable reviews={reviews} />
        </Panel>
      </section>
    </AppShell>
  );
}
