from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.evaluation import EvaluationResponse

ModelRunStatus = Literal["executed", "failed", "blocked", "requires_review"]


class RetrievedDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    model_run_id: UUID
    source_label: str
    content: str
    ordinal: int
    created_at: datetime


class ModelRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ai_system_id: UUID
    prompt_version_id: UUID | None
    prompt: str
    input_text: str
    output_text: str | None
    model_provider: str
    model_name: str
    model_version: str
    latency_ms: int
    cost_usd: float
    status: ModelRunStatus
    input_pii_result: dict
    output_pii_result: dict
    created_at: datetime
    retrieved_documents: list[RetrievedDocumentResponse] = []
    evaluation: EvaluationResponse | None = None
