export type DashboardMetric = {
  label: string;
  value: string;
  trend: string;
  tone: "neutral" | "trust" | "warning" | "critical";
};

export type RiskLevel = "low" | "medium" | "high" | "critical";
export type ApprovalStatus = "pending" | "approved" | "blocked" | "retired";

export type AISystem = {
  id: string;
  name: string;
  description: string;
  department: string;
  owner_name: string;
  owner_email: string;
  model_provider: string;
  model_name: string;
  data_sources: string[];
  contains_personal_data: boolean;
  risk_level: RiskLevel;
  human_oversight_required: boolean;
  approval_status: ApprovalStatus;
  created_at: string;
  updated_at: string;
};

export type AISystemCreate = Omit<AISystem, "id" | "created_at" | "updated_at">;
