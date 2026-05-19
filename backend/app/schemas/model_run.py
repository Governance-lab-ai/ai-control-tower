from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

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
    output_text: str
    model_provider: str
    model_name: str
    model_version: str
    latency_ms: int
    cost_usd: float
    status: ModelRunStatus
    created_at: datetime
    retrieved_documents: list[RetrievedDocumentResponse] = []
