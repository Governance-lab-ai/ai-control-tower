export type DashboardMetric = {
  label: string;
  value: string;
  trend: string;
  tone: "neutral" | "trust" | "warning" | "critical";
};

export type RiskHeatmapCell = {
  department: string;
  risk_level: RiskLevel;
  count: number;
};

export type ModelUsageSummary = {
  model_provider: string;
  model_name: string;
  total_runs: number;
  total_cost_usd: number;
  average_latency_ms: number;
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
  prompt_version_id?: string | null;
  actor: string;
  prompt: string;
  input_text: string;
  retrieved_documents?: string[];
  metadata?: Record<string, unknown>;
};

export type PromptVersionStatus = "draft" | "approved" | "active" | "retired";

export type PromptVersion = {
  id: string;
  ai_system_id: string;
  version: string;
  name: string;
  prompt_text: string;
  status: PromptVersionStatus;
  created_at: string;
};

export type PromptVersionCreate = {
  version?: string | null;
  name: string;
  prompt_text: string;
  status?: PromptVersionStatus;
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

export type RunStep = {
  id: string;
  model_run_id: string;
  step_type: string;
  name: string;
  status: string;
  input_summary: string | null;
  output_summary: string | null;
  metadata: Record<string, unknown>;
  latency_ms: number | null;
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
  run_steps: RunStep[];
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

export type IncidentUpdateRequest = {
  status: IncidentStatus;
  actor: string;
  notes?: string;
};

export type AuditEvent = {
  id: string;
  actor: string;
  action: string;
  entity_type: string;
  entity_id: string;
  summary: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type HumanReviewStatus = "pending" | "approved" | "rejected" | "escalated";
export type HumanReviewDecision = "approved" | "rejected" | "escalated";
export type HumanReviewPriority = "low" | "medium" | "high" | "critical";

export type HumanReview = {
  id: string;
  ai_system_id: string;
  model_run_id: string;
  status: HumanReviewStatus;
  reason: string;
  priority: HumanReviewPriority;
  summary: string;
  reviewer_id: string | null;
  reviewer_name: string | null;
  decision_notes: string | null;
  decided_at: string | null;
  created_at: string;
  updated_at: string;
};

export type HumanReviewDetail = HumanReview & {
  model_run: ModelRun;
};

export type HumanReviewDecisionRequest = {
  decision: HumanReviewDecision;
  reviewer_id: string;
  reviewer_name: string;
  notes: string;
};

export type EvidencePack = {
  generated_at: string;
  evidence_pack_version: string;
  run_id: string;
  ai_system: AISystem;
  prompt_version: PromptVersion | null;
  model_run: ModelRun;
  incidents: Incident[];
  human_reviews: HumanReview[];
  audit_events: AuditEvent[];
};

export type DashboardSummary = {
  total_ai_systems: number;
  systems_by_risk: Record<RiskLevel, number>;
  systems_by_department: Record<string, number>;
  pending_reviews: number;
  open_incidents: number;
  failed_evaluations: number;
  total_runs: number;
  total_cost_usd: number;
  average_latency_ms: number;
  risk_heatmap: RiskHeatmapCell[];
  incidents_by_severity: Partial<Record<IncidentSeverity, number>>;
  incidents_by_type: Record<string, number>;
  usage_by_model: ModelUsageSummary[];
  recent_incidents: Incident[];
  recent_failed_evaluations: Evaluation[];
};
