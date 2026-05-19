import type { ApprovalStatus, RiskLevel } from "@/lib/types";

export const RISK_LEVELS = ["low", "medium", "high", "critical"] as const satisfies readonly RiskLevel[];
export const APPROVAL_STATUSES = ["pending", "approved", "blocked", "retired"] as const satisfies readonly ApprovalStatus[];

export function splitCommaList(value: string): string[] {
  return value
    .split(",")
    .map((source) => source.trim())
    .filter(Boolean);
}
