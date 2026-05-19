from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

GatewayStatus = Literal["executed", "blocked", "requires_review", "failed"]


class GovernanceRunRequest(BaseModel):
    ai_system_id: UUID
    actor: str = Field(min_length=2, max_length=160)
    prompt: str = Field(min_length=1, max_length=12000)
    input_text: str = Field(min_length=1, max_length=12000)
    retrieved_documents: list[str] = Field(default_factory=list, max_length=20)
    metadata: dict = Field(default_factory=dict)


class GovernanceRunResponse(BaseModel):
    run_id: UUID | None = None
    status: GatewayStatus
    output_text: str | None = None
    governance_messages: list[str]
