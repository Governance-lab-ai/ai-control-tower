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

export type PIIResult = {
  pii_detected?: boolean;
  pii_types?: string[];
  locations?: Array<{
    pii_type: string;
    snippet: string;
    start: number;
    end: number;
  }>;
  confidence?: "low" | "medium" | "high";
};

export type Evaluation = {
  id: string;
  model_run_id: string;
  ai_system_id: string;
  provider: string;
  evaluation_score: number;
  relevance_score: number;
  groundedness_score: number;
  hallucination_flag: boolean;
  evaluation_summary: string;
  requires_human_review: boolean;
  threshold: number;
  created_at: string;
};

export type ModelRun = {
  id: string;
  ai_system_id: string;
  prompt_version_id: string | null;
  prompt: string;
  input_text: string;
  output_text: string | null;
  model_provider: string;
  model_name: string;
  model_version: string;
  latency_ms: number;
  cost_usd: number;
  status: ModelRunStatus;
  input_pii_result: PIIResult;
  output_pii_result: PIIResult;
  created_at: string;
  retrieved_documents: RetrievedDocument[];
  evaluation: Evaluation | null;
};

export type IncidentStatus = "open" | "under_review" | "resolved" | "dismissed";
export type IncidentSeverity = "low" | "medium" | "high" | "critical";

export type Incident = {
  id: string;
  ai_system_id: string;
  model_run_id: string | null;
  incident_type: string;
  severity: IncidentSeverity;
  title: string;
  description: string;
  status: IncidentStatus;
  created_at: string;
  updated_at: string;
};
