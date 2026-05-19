import { StatusBadge } from "@/components/status-badge";
import type { IncidentSeverity, IncidentStatus } from "@/lib/types";

const severityTone: Record<IncidentSeverity, "neutral" | "warning" | "critical" | "rose"> = {
  low: "neutral",
  medium: "warning",
  high: "rose",
  critical: "critical",
};

const statusTone: Record<IncidentStatus, "neutral" | "warning" | "trust"> = {
  open: "warning",
  under_review: "neutral",
  resolved: "trust",
  dismissed: "neutral",
};

export function IncidentSeverityBadge({ severity }: { severity: IncidentSeverity }) {
  return <StatusBadge label={severity.replace("_", " ")} tone={severityTone[severity]} />;
}

export function IncidentStatusBadge({ status }: { status: IncidentStatus }) {
  return <StatusBadge label={status.replace("_", " ")} tone={statusTone[status]} />;
}
