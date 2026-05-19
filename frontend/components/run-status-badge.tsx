import { StatusBadge } from "@/components/status-badge";
import type { ModelRunStatus } from "@/lib/types";

const labels: Record<ModelRunStatus, string> = {
  executed: "Executed",
  failed: "Failed",
  blocked: "Blocked",
  requires_review: "Requires review",
};

const tones: Record<ModelRunStatus, "trust" | "critical" | "warning" | "neutral"> = {
  executed: "trust",
  failed: "critical",
  blocked: "critical",
  requires_review: "warning",
};

export function RunStatusBadge({ status }: { status: ModelRunStatus }) {
  return <StatusBadge label={labels[status]} tone={tones[status]} />;
}
