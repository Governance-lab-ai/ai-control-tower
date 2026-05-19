import { Activity, AlertTriangle, ClipboardCheck, Database, FileClock, Gauge, Settings, ShieldCheck } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { StatusBadge } from "@/components/status-badge";
import type { DashboardMetric } from "@/lib/types";

const metrics: DashboardMetric[] = [
  { label: "Registered AI systems", value: "12", trend: "+3 this month", tone: "neutral" },
  { label: "Governance posture", value: "72 / 100", trend: "Needs evidence review", tone: "trust" },
  { label: "Pending approvals", value: "4", trend: "2 high impact", tone: "warning" },
  { label: "Open reviews", value: "9", trend: "Oldest 18h", tone: "warning" },
  { label: "Critical incidents", value: "1", trend: "PII exposure", tone: "critical" },
];

const recentRuns = [
  ["run_1048", "Support Summariser", "allow_with_review", "Medium", "2 min ago"],
  ["run_1047", "Claims Triage Assistant", "hold_for_review", "High", "11 min ago"],
  ["run_1046", "Policy Draft Helper", "allow", "Low", "24 min ago"],
  ["run_1045", "Sales Email Generator", "block", "Critical", "41 min ago"],
];

const navItems = [
  { label: "Dashboard", icon: Gauge, active: true },
  { label: "AI Systems", icon: Database },
  { label: "Runs", icon: Activity },
  { label: "Reviews", icon: ClipboardCheck },
  { label: "Incidents", icon: AlertTriangle },
  { label: "Audit", icon: FileClock },
  { label: "Settings", icon: Settings },
];

export default function DashboardPage() {
  return (
    <AppShell navItems={navItems}>
      <section className="flex flex-col gap-2 border-b border-line-700/80 px-5 py-5 md:px-8">
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.04em] text-trust-teal">Local command centre</p>
            <h1 className="mt-2 text-2xl font-semibold text-[#E6EEF8] md:text-[28px]">AI Governance Dashboard</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-[#A8B8CA]">
              Monitor registered systems, governed model runs, review queues, incidents, and audit readiness from one operational surface.
            </p>
          </div>
          <div className="flex items-center gap-2 rounded-lg border border-line-700 bg-panel-875 px-3 py-2 text-sm text-[#A8B8CA]">
            <ShieldCheck className="h-4 w-4 text-trust-teal" aria-hidden="true" />
            <span>Mock identity: Governance Admin</span>
          </div>
        </div>
      </section>

      <section className="grid gap-4 px-5 py-5 md:grid-cols-5 md:px-8">
        {metrics.map((metric) => (
          <article key={metric.label} className="rounded-lg border border-line-700 bg-panel-875/90 p-4 shadow-panel">
            <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">{metric.label}</p>
            <div className="mt-3 flex items-baseline justify-between gap-3">
              <p className="text-2xl font-semibold text-[#E6EEF8]">{metric.value}</p>
              <span className={metricToneClass(metric.tone)}>{metric.trend}</span>
            </div>
          </article>
        ))}
      </section>

      <section className="grid gap-4 px-5 pb-8 md:grid-cols-12 md:px-8">
        <article className="rounded-lg border border-line-700 bg-panel-875/90 p-5 shadow-panel md:col-span-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-[#E6EEF8]">Risk Posture</h2>
            <StatusBadge label="Review required" tone="warning" />
          </div>
          <div className="mt-6 flex items-end gap-3">
            {["Low", "Medium", "High", "Critical"].map((level, index) => (
              <div key={level} className="flex flex-1 flex-col gap-2">
                <div
                  className="rounded-md border border-line-700 bg-panel-825"
                  style={{ height: `${72 + index * 26}px` }}
                  aria-label={`${level} risk bar`}
                />
                <span className="text-xs text-[#A8B8CA]">{level}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="rounded-lg border border-line-700 bg-panel-875/90 p-5 shadow-panel md:col-span-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-[#E6EEF8]">Review Queue</h2>
            <StatusBadge label="9 waiting" tone="critical" />
          </div>
          <div className="mt-5 space-y-3">
            {["Claims Triage Assistant", "Support Summariser", "Contract Review Helper"].map((system, index) => (
              <div key={system} className="rounded-lg border border-line-700 bg-panel-825/70 p-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-medium text-[#E6EEF8]">{system}</p>
                  <StatusBadge label={index === 0 ? "High" : "Medium"} tone={index === 0 ? "critical" : "warning"} />
                </div>
                <p className="mt-2 text-xs text-[#A8B8CA]">Evaluation evidence and reviewer decision pending.</p>
              </div>
            ))}
          </div>
        </article>

        <article className="rounded-lg border border-line-700 bg-panel-875/90 p-5 shadow-panel md:col-span-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-[#E6EEF8]">Integration State</h2>
            <StatusBadge label="Local" tone="trust" />
          </div>
          <dl className="mt-5 space-y-3 text-sm">
            <div className="flex justify-between gap-4 border-b border-line-700/70 pb-3">
              <dt className="text-[#A8B8CA]">Model provider</dt>
              <dd className="font-mono text-[#E6EEF8]">mock</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-line-700/70 pb-3">
              <dt className="text-[#A8B8CA]">Safety provider</dt>
              <dd className="font-mono text-[#E6EEF8]">local</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-[#A8B8CA]">Audit mode</dt>
              <dd className="font-mono text-[#E6EEF8]">append-only planned</dd>
            </div>
          </dl>
        </article>

        <article className="rounded-lg border border-line-700 bg-panel-875/90 shadow-panel md:col-span-12">
          <div className="border-b border-line-700 px-5 py-4">
            <h2 className="text-base font-semibold text-[#E6EEF8]">Recent Governed Runs</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-navy-900/70 text-xs uppercase tracking-[0.04em] text-[#718198]">
                <tr>
                  <th className="px-5 py-3 font-semibold">Run ID</th>
                  <th className="px-5 py-3 font-semibold">System</th>
                  <th className="px-5 py-3 font-semibold">Route</th>
                  <th className="px-5 py-3 font-semibold">Risk</th>
                  <th className="px-5 py-3 font-semibold">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line-700">
                {recentRuns.map(([runId, system, route, risk, time]) => (
                  <tr key={runId} className="hover:bg-panel-825/60">
                    <td className="px-5 py-4 font-mono text-xs text-signal-cyan">{runId}</td>
                    <td className="px-5 py-4 text-[#E6EEF8]">{system}</td>
                    <td className="px-5 py-4 font-mono text-xs text-[#A8B8CA]">{route}</td>
                    <td className="px-5 py-4">
                      <StatusBadge label={risk} tone={risk === "Critical" ? "critical" : risk === "High" ? "warning" : "trust"} />
                    </td>
                    <td className="px-5 py-4 text-[#A8B8CA]">{time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </section>
    </AppShell>
  );
}

function metricToneClass(tone: DashboardMetric["tone"]): string {
  const base = "rounded-md px-2 py-1 text-xs";
  if (tone === "critical") return `${base} bg-red-500/15 text-red-200`;
  if (tone === "warning") return `${base} bg-amber-500/15 text-amber-200`;
  if (tone === "trust") return `${base} bg-emerald-500/15 text-emerald-200`;
  return `${base} bg-slate-500/15 text-slate-200`;
}
