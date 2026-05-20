import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { getAuditEvents } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { getNavItems } from "@/lib/navigation";

export default async function AuditPage() {
  const events = await getAuditEvents();

  return (
    <AppShell navItems={getNavItems("Audit")}>
      <PageHeader
        kicker="Evidence Ledger"
        title="Audit Events"
        description="Append-only governance events for registry, gateway, incident, evaluation, and reviewer actions."
      />

      <section className="px-5 py-5 md:px-8">
        <Panel>
          {events.length === 0 ? (
            <p className="p-5 text-sm text-[#A8B8CA]">No audit events recorded.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-navy-900/70 text-xs uppercase tracking-[0.04em] text-[#718198]">
                  <tr>
                    <th className="px-5 py-3 font-semibold">Event</th>
                    <th className="px-5 py-3 font-semibold">Actor</th>
                    <th className="px-5 py-3 font-semibold">Entity</th>
                    <th className="px-5 py-3 font-semibold">Created</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line-700">
                  {events.map((event) => (
                    <tr key={event.id} className="align-top hover:bg-panel-825/60">
                      <td className="px-5 py-4">
                        <p className="font-mono text-xs text-signal-cyan">{event.action}</p>
                        <p className="mt-1 max-w-2xl text-sm text-[#E6EEF8]">{event.summary}</p>
                        {Object.keys(event.metadata ?? {}).length > 0 ? (
                          <pre className="mt-3 max-h-36 overflow-auto rounded-md border border-line-700 bg-navy-900 p-3 text-xs leading-5 text-[#A8B8CA]">
                            {JSON.stringify(event.metadata, null, 2)}
                          </pre>
                        ) : null}
                      </td>
                      <td className="px-5 py-4 font-mono text-xs text-[#A8B8CA]">{event.actor}</td>
                      <td className="px-5 py-4">
                        <p className="font-mono text-xs text-[#A8B8CA]">{event.entity_type}</p>
                        {event.entity_type === "model_run" ? (
                          <Link href={`/runs/${event.entity_id}`} className="mt-1 block font-mono text-xs text-signal-cyan hover:text-[#E6EEF8]">
                            {event.entity_id.slice(0, 8)}
                          </Link>
                        ) : (
                          <p className="mt-1 font-mono text-xs text-[#718198]">{event.entity_id.slice(0, 8)}</p>
                        )}
                      </td>
                      <td className="px-5 py-4 text-[#A8B8CA]">{formatDateTime(event.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
      </section>
    </AppShell>
  );
}
