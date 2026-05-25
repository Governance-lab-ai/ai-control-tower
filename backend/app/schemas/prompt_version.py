from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

PromptVersionStatus = Literal["draft", "approved", "active", "retired"]


class PromptVersionCreate(BaseModel):
    version: str | None = Field(default=None, max_length=40)
    name: str = Field(min_length=2, max_length=160)
    prompt_text: str = Field(min_length=1, max_length=12000)
    status: PromptVersionStatus = "draft"


class PromptVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ai_system_id: UUID
    version: str
    name: str
    prompt_text: str
    status: PromptVersionStatus
    created_at: datetime
