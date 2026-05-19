from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.model_run import ModelRunResponse

HumanReviewStatus = Literal["pending", "approved", "rejected", "escalated"]
HumanReviewDecision = Literal["approved", "rejected", "escalated"]
HumanReviewPriority = Literal["low", "medium", "high", "critical"]


class HumanReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ai_system_id: UUID
    model_run_id: UUID
    status: HumanReviewStatus
    reason: str
    priority: HumanReviewPriority
    summary: str
    reviewer_id: str | None
    reviewer_name: str | None
    decision_notes: str | None
    decided_at: datetime | None
    created_at: datetime
    updated_at: datetime


class HumanReviewDetailResponse(HumanReviewResponse):
    model_run: ModelRunResponse


class HumanReviewDecisionRequest(BaseModel):
    decision: HumanReviewDecision
    reviewer_id: str = Field(min_length=1, max_length=120)
    reviewer_name: str = Field(min_length=1, max_length=160)
    notes: str = Field(min_length=1, max_length=4000)
