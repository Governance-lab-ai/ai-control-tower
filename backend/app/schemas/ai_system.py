from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

RiskLevel = Literal["low", "medium", "high", "critical"]
ApprovalStatus = Literal["pending", "approved", "blocked", "retired"]


class AISystemCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(min_length=10, max_length=4000)
    department: str = Field(min_length=2, max_length=120)
    owner_name: str = Field(min_length=2, max_length=120)
    owner_email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    model_provider: str = Field(min_length=2, max_length=80)
    model_name: str = Field(min_length=2, max_length=120)
    data_sources: list[str] = Field(default_factory=list, max_length=20)
    contains_personal_data: bool
    risk_level: RiskLevel
    human_oversight_required: bool
    approval_status: ApprovalStatus = "pending"


class AISystemResponse(AISystemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class ApprovalStatusUpdate(BaseModel):
    approval_status: ApprovalStatus
