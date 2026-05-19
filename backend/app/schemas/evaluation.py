from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    model_run_id: UUID
    ai_system_id: UUID
    provider: str
    evaluation_score: int = Field(ge=0, le=100)
    relevance_score: int = Field(ge=0, le=100)
    groundedness_score: int = Field(ge=0, le=100)
    hallucination_flag: bool
    evaluation_summary: str
    requires_human_review: bool
    threshold: int = Field(ge=0, le=100)
    created_at: datetime
