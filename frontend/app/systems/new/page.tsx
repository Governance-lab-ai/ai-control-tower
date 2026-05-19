import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/ui/page-header";
import { getNavItems } from "@/lib/navigation";
import { SystemForm } from "./system-form";

export default function NewSystemPage() {
  return (
    <AppShell navItems={getNavItems("AI Systems")}>
      <PageHeader
        title="Register AI System"
        description="Capture owner, model, data exposure, risk, oversight, and approval state before a system can move through governed runtime paths."
        backLink={
          <Link href="/systems" className="text-sm text-signal-cyan hover:text-[#E6EEF8]">
            Back to registry
          </Link>
        }
      />
      <section className="px-5 py-5 md:px-8">
        <SystemForm />
      </section>
    </AppShell>
  );
}
