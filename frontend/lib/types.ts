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

export type GovernanceRunStatus = "executed" | "blocked" | "requires_review" | "failed";

export type GovernanceRunRequest = {
  ai_system_id: string;
  actor: string;
  prompt: string;
  input_text: string;
  retrieved_documents?: string[];
  metadata?: Record<string, unknown>;
};

export type GovernanceRunResponse = {
  run_id: string | null;
  status: GovernanceRunStatus;
  output_text: string | null;
  governance_messages: string[];
};

export type RetrievedDocument = {
  id: string;
  model_run_id: string;
  source_label: string;
  content: string;
  ordinal: number;
  created_at: string;
};

export type ModelRunStatus = "executed" | "failed" | "blocked" | "requires_review";

export type ModelRun = {
  id: string;
  ai_system_id: string;
  prompt_version_id: string | null;
  prompt: string;
  input_text: string;
  output_text: string;
  model_provider: string;
  model_name: string;
  model_version: string;
  latency_ms: number;
  cost_usd: number;
  status: ModelRunStatus;
  created_at: string;
  retrieved_documents: RetrievedDocument[];
};
