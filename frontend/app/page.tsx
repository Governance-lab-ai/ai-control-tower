import Link from "next/link";
import { AlertTriangle, BarChart3, Clock3, DollarSign, FileWarning, ShieldCheck, type LucideIcon } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { EvaluationBadge } from "@/components/evaluation-badge";
import { IncidentSeverityBadge } from "@/components/incident-badges";
import { StatusBadge } from "@/components/status-badge";
import { Panel } from "@/components/ui/panel";
import { getDashboardSummary } from "@/lib/api";
import { formatCurrencyUsd, formatDateTime, formatLatency } from "@/lib/format";
import { getNavItems } from "@/lib/navigation";
import type { DashboardMetric, DashboardSummary, IncidentSeverity, RiskLevel } from "@/lib/types";

const riskLevels: RiskLevel[] = ["low", "medium", "high", "critical"];

export default async function DashboardPage() {
  const summary = await getDashboardSummary();
  const metrics = dashboardMetrics(summary);
  const departments = Array.from(new Set(summary.risk_heatmap.map((cell) => cell.department))).sort();
  const highestHeatmapCount = Math.max(1, ...summary.risk_heatmap.map((cell) => cell.count));

  return (
    <AppShell navItems={getNavItems("Dashboard")}>
      <section className="border-b border-line-700/80 px-5 py-5 md:px-8">
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.04em] text-trust-teal">Control Tower</p>
            <h1 className="mt-2 text-2xl font-semibold text-[#E6EEF8] md:text-[28px]">Governance Overview</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-[#A8B8CA]">
              Live operating view across registered AI systems, governed runs, risk signals, incidents, reviews, and audit evidence.
            </p>
          </div>
          <Link
            href="/audit"
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-line-700 bg-panel-875 px-3 py-2 text-sm font-semibold text-[#E6EEF8] hover:border-trust-teal/70"
          >
            <FileWarning className="h-4 w-4 text-trust-teal" aria-hidden="true" />
            Audit Export
          </Link>
        </div>
      </section>

      <section className="grid gap-4 px-5 py-5 md:grid-cols-5 md:px-8">
        {metrics.map((metric) => (
          <article key={metric.label} className="rounded-lg border border-line-700 bg-panel-875/90 p-4 shadow-panel">
            <div className="flex items-center justify-between gap-3">
              <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">{metric.label}</p>
              <metric.icon className="h-4 w-4 text-[#718198]" aria-hidden="true" />
            </div>
            <div className="mt-3 flex items-end justify-between gap-3">
              <p className="text-2xl font-semibold text-[#E6EEF8]">{metric.value}</p>
              <span className={metricToneClass(metric.tone)}>{metric.trend}</span>
            </div>
          </article>
        ))}
      </section>

      <section className="grid gap-4 px-5 pb-8 md:grid-cols-12 md:px-8">
        <Panel className="p-5 md:col-span-7">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-semibold text-[#E6EEF8]">Risk Heatmap</h2>
              <p className="mt-1 text-sm text-[#A8B8CA]">Registered systems by department and risk level.</p>
            </div>
            <StatusBadge label={`${summary.total_ai_systems} systems`} tone="neutral" />
          </div>

          <div className="mt-5 overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="text-xs uppercase tracking-[0.04em] text-[#718198]">
                <tr>
                  <th className="w-48 py-2 pr-3 font-semibold">Department</th>
                  {riskLevels.map((riskLevel) => (
                    <th key={riskLevel} className="px-2 py-2 text-center font-semibold">
                      {riskLevel}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-line-700">
                {departments.length === 0 ? (
                  <tr>
                    <td className="py-5 text-sm text-[#A8B8CA]" colSpan={5}>
                      No registered systems yet.
                    </td>
                  </tr>
                ) : (
                  departments.map((department) => (
                    <tr key={department}>
                      <td className="py-3 pr-3 font-medium text-[#E6EEF8]">{department}</td>
                      {riskLevels.map((riskLevel) => {
                        const count = summary.risk_heatmap.find((cell) => cell.department === department && cell.risk_level === riskLevel)?.count ?? 0;
                        return (
                          <td key={riskLevel} className="px-2 py-3">
                            <div className={`rounded-md border px-3 py-2 text-center font-mono text-sm ${heatmapCellClass(riskLevel, count, highestHeatmapCount)}`}>
                              {count}
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel className="p-5 md:col-span-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-[#E6EEF8]">Incident Summary</h2>
              <p className="mt-1 text-sm text-[#A8B8CA]">Active incident load by type and severity.</p>
            </div>
            <StatusBadge label={`${summary.open_incidents} active`} tone={summary.open_incidents > 0 ? "warning" : "trust"} />
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {Object.entries(summary.incidents_by_severity).length === 0 ? (
              <p className="text-sm text-[#A8B8CA]">No active incidents.</p>
            ) : (
              Object.entries(summary.incidents_by_severity).map(([severity, count]) => (
                <div key={severity} className="rounded-lg border border-line-700 bg-panel-825/70 p-3">
                  <IncidentSeverityBadge severity={severity as IncidentSeverity} />
                  <p className="mt-3 text-2xl font-semibold text-[#E6EEF8]">{count}</p>
                </div>
              ))
            )}
          </div>
          <div className="mt-5 space-y-2">
            {Object.entries(summary.incidents_by_type).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between gap-4 border-b border-line-700/70 pb-2 text-sm">
                <span className="font-mono text-xs text-[#A8B8CA]">{type}</span>
                <span className="font-semibold text-[#E6EEF8]">{count}</span>
              </div>
            ))}
          </div>
        </Panel>

        <Panel className="md:col-span-6">
          <div className="border-b border-line-700 px-5 py-4">
            <h2 className="text-base font-semibold text-[#E6EEF8]">Failed Evaluations</h2>
          </div>
          {summary.recent_failed_evaluations.length === 0 ? (
            <p className="p-5 text-sm text-[#A8B8CA]">No failed evaluations recorded.</p>
          ) : (
            <div className="divide-y divide-line-700">
              {summary.recent_failed_evaluations.map((evaluation) => (
                <Link key={evaluation.id} href={`/runs/${evaluation.model_run_id}`} className="block px-5 py-4 hover:bg-panel-825/60">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-mono text-xs text-signal-cyan">{evaluation.model_run_id.slice(0, 8)}</p>
                      <p className="mt-2 max-w-xl text-sm leading-5 text-[#A8B8CA]">{evaluation.evaluation_summary}</p>
                    </div>
                    <EvaluationBadge evaluation={evaluation} />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </Panel>

        <Panel className="md:col-span-6">
          <div className="border-b border-line-700 px-5 py-4">
            <h2 className="text-base font-semibold text-[#E6EEF8]">Recent Incidents</h2>
          </div>
          {summary.recent_incidents.length === 0 ? (
            <p className="p-5 text-sm text-[#A8B8CA]">No active incidents recorded.</p>
          ) : (
            <div className="divide-y divide-line-700">
              {summary.recent_incidents.map((incident) => (
                <Link key={incident.id} href={`/incidents/${incident.id}`} className="block px-5 py-4 hover:bg-panel-825/60">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-sm font-medium text-[#E6EEF8]">{incident.title}</p>
                      <p className="mt-1 font-mono text-xs text-[#718198]">{incident.incident_type}</p>
                      <p className="mt-2 text-xs text-[#A8B8CA]">{formatDateTime(incident.created_at)}</p>
                    </div>
                    <IncidentSeverityBadge severity={incident.severity} />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </Panel>

        <Panel className="p-5 md:col-span-12">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-base font-semibold text-[#E6EEF8]">Model Usage And Cost</h2>
              <p className="mt-1 text-sm text-[#A8B8CA]">Run volume, estimated spend, and observed latency by provider/model.</p>
            </div>
            <StatusBadge label={formatCurrencyUsd(summary.total_cost_usd)} tone="trust" />
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {summary.usage_by_model.length === 0 ? (
              <p className="text-sm text-[#A8B8CA]">No model runs recorded.</p>
            ) : (
              summary.usage_by_model.map((item) => (
                <div key={`${item.model_provider}:${item.model_name}`} className="rounded-lg border border-line-700 bg-panel-825/70 p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="font-mono text-xs text-signal-cyan">{item.model_provider}</p>
                      <p className="mt-1 text-sm font-semibold text-[#E6EEF8]">{item.model_name}</p>
                    </div>
                    <StatusBadge label={`${item.total_runs} runs`} tone="neutral" />
                  </div>
                  <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <p className="text-xs uppercase tracking-[0.04em] text-[#718198]">Cost</p>
                      <p className="mt-1 font-mono text-[#E6EEF8]">{formatCurrencyUsd(item.total_cost_usd)}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.04em] text-[#718198]">Avg latency</p>
                      <p className="mt-1 font-mono text-[#E6EEF8]">{formatLatency(Math.round(item.average_latency_ms))}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </Panel>
      </section>
    </AppShell>
  );
}

function dashboardMetrics(summary: DashboardSummary): Array<DashboardMetric & { icon: LucideIcon }> {
  return [
    { label: "AI systems", value: String(summary.total_ai_systems), trend: `${summary.systems_by_risk.high + summary.systems_by_risk.critical} high+`, tone: "neutral", icon: ShieldCheck },
    { label: "Pending reviews", value: String(summary.pending_reviews), trend: "human queue", tone: summary.pending_reviews > 0 ? "warning" : "trust", icon: Clock3 },
    { label: "Open incidents", value: String(summary.open_incidents), trend: "active risk", tone: summary.open_incidents > 0 ? "critical" : "trust", icon: AlertTriangle },
    { label: "Failed evals", value: String(summary.failed_evaluations), trend: "review signals", tone: summary.failed_evaluations > 0 ? "warning" : "trust", icon: BarChart3 },
    { label: "Run cost", value: formatCurrencyUsd(summary.total_cost_usd), trend: `${summary.total_runs} runs`, tone: "trust", icon: DollarSign },
  ];
}

function metricToneClass(tone: DashboardMetric["tone"]): string {
  const base = "rounded-md px-2 py-1 text-xs";
  if (tone === "critical") return `${base} bg-red-500/15 text-red-200`;
  if (tone === "warning") return `${base} bg-amber-500/15 text-amber-200`;
  if (tone === "trust") return `${base} bg-emerald-500/15 text-emerald-200`;
  return `${base} bg-slate-500/15 text-slate-200`;
}

function heatmapCellClass(riskLevel: RiskLevel, count: number, highestCount: number): string {
  if (count === 0) return "border-line-700 bg-navy-900/80 text-[#718198]";
  const strong = count / highestCount >= 0.75;
  if (riskLevel === "critical") return strong ? "border-red-400/50 bg-red-500/35 text-red-50" : "border-red-400/30 bg-red-500/18 text-red-100";
  if (riskLevel === "high") return strong ? "border-amber-400/50 bg-amber-500/35 text-amber-50" : "border-amber-400/30 bg-amber-500/18 text-amber-100";
  if (riskLevel === "medium") return strong ? "border-cyan-400/45 bg-cyan-500/25 text-cyan-50" : "border-cyan-400/25 bg-cyan-500/12 text-cyan-100";
  return strong ? "border-emerald-400/45 bg-emerald-500/25 text-emerald-50" : "border-emerald-400/25 bg-emerald-500/12 text-emerald-100";
}
