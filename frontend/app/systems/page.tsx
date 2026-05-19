import Link from "next/link";
import { Plus } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { ApprovalBadge, RiskBadge } from "@/components/registry-badges";
import { ActionLink } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { getSystems } from "@/lib/api";
import { formatBooleanYesNo } from "@/lib/format";
import { getNavItems } from "@/lib/navigation";

export default async function SystemsPage() {
  const systems = await getSystems();

  return (
    <AppShell navItems={getNavItems("AI Systems")}>
      <PageHeader
        kicker="Registry"
        title="AI Systems"
        description="Governed inventory of organisational AI systems, owners, models, data exposure, risk, and approval state."
        action={
          <ActionLink href="/systems/new">
            <Plus className="h-4 w-4" aria-hidden="true" />
            Register AI System
          </ActionLink>
        }
      />

      <section className="px-5 py-5 md:px-8">
        <Panel>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-navy-900/70 text-xs uppercase tracking-[0.04em] text-[#718198]">
                <tr>
                  <th className="px-5 py-3 font-semibold">System</th>
                  <th className="px-5 py-3 font-semibold">Department</th>
                  <th className="px-5 py-3 font-semibold">Owner</th>
                  <th className="px-5 py-3 font-semibold">Model</th>
                  <th className="px-5 py-3 font-semibold">Personal data</th>
                  <th className="px-5 py-3 font-semibold">Risk</th>
                  <th className="px-5 py-3 font-semibold">Approval</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line-700">
                {systems.map((system) => (
                  <tr key={system.id} className="hover:bg-panel-825/60">
                    <td className="px-5 py-4">
                      <Link href={`/systems/${system.id}`} className="font-medium text-signal-cyan hover:text-[#E6EEF8]">
                        {system.name}
                      </Link>
                      <p className="mt-1 max-w-sm truncate text-xs text-[#A8B8CA]">{system.description}</p>
                    </td>
                    <td className="px-5 py-4 text-[#E6EEF8]">{system.department}</td>
                    <td className="px-5 py-4">
                      <p className="text-[#E6EEF8]">{system.owner_name}</p>
                      <p className="font-mono text-xs text-[#A8B8CA]">{system.owner_email}</p>
                    </td>
                    <td className="px-5 py-4">
                      <p className="text-[#E6EEF8]">{system.model_provider}</p>
                      <p className="font-mono text-xs text-[#A8B8CA]">{system.model_name}</p>
                    </td>
                    <td className="px-5 py-4 text-[#A8B8CA]">{formatBooleanYesNo(system.contains_personal_data)}</td>
                    <td className="px-5 py-4">
                      <RiskBadge level={system.risk_level} />
                    </td>
                    <td className="px-5 py-4">
                      <ApprovalBadge status={system.approval_status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </section>
    </AppShell>
  );
}
