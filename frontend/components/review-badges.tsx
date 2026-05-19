import { StatusBadge } from "@/components/status-badge";
import type { HumanReviewPriority, HumanReviewStatus } from "@/lib/types";

const priorityTone: Record<HumanReviewPriority, "neutral" | "warning" | "critical" | "rose"> = {
  low: "neutral",
  medium: "warning",
  high: "rose",
  critical: "critical",
};

const statusTone: Record<HumanReviewStatus, "neutral" | "warning" | "trust" | "critical" | "rose"> = {
  pending: "warning",
  approved: "trust",
  rejected: "critical",
  escalated: "rose",
};

export function ReviewPriorityBadge({ priority }: { priority: HumanReviewPriority }) {
  return <StatusBadge label={priority} tone={priorityTone[priority]} />;
}

export function ReviewStatusBadge({ status }: { status: HumanReviewStatus }) {
  return <StatusBadge label={status.replace("_", " ")} tone={statusTone[status]} />;
}
