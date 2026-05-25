from pydantic import BaseModel, Field

from app.schemas.evaluation import EvaluationResponse
from app.schemas.incident import IncidentResponse


class RiskHeatmapCell(BaseModel):
    department: str
    risk_level: str
    count: int


class ModelUsageSummary(BaseModel):
    model_provider: str
    model_name: str
    total_runs: int
    total_cost_usd: float
    average_latency_ms: float


class DashboardSummaryResponse(BaseModel):
    total_ai_systems: int
    systems_by_risk: dict[str, int] = Field(default_factory=dict)
    systems_by_department: dict[str, int] = Field(default_factory=dict)
    pending_reviews: int
    open_incidents: int
    failed_evaluations: int
    total_runs: int
    total_cost_usd: float
    average_latency_ms: float
    risk_heatmap: list[RiskHeatmapCell] = Field(default_factory=list)
    incidents_by_severity: dict[str, int] = Field(default_factory=dict)
    incidents_by_type: dict[str, int] = Field(default_factory=dict)
    usage_by_model: list[ModelUsageSummary] = Field(default_factory=list)
    recent_incidents: list[IncidentResponse] = Field(default_factory=list)
    recent_failed_evaluations: list[EvaluationResponse] = Field(default_factory=list)
