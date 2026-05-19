import type { ApprovalStatus, RiskLevel } from "@/lib/types";
import { Badge, type BadgeTone } from "@/components/ui/badge";

const riskTone: Record<RiskLevel, BadgeTone> = {
  low: "trust",
  medium: "warning",
  high: "orange",
  critical: "critical",
};

const approvalTone: Record<ApprovalStatus, BadgeTone> = {
  pending: "warning",
  approved: "trust",
  blocked: "rose",
  retired: "neutral",
};

export function RiskBadge({ level }: { level: RiskLevel }) {
  return (
    <Badge tone={riskTone[level]} className="capitalize">
      {level}
    </Badge>
  );
}

export function ApprovalBadge({ status }: { status: ApprovalStatus }) {
  return (
    <Badge tone={approvalTone[status]} className="capitalize">
      {status}
    </Badge>
  );
}
