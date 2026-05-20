from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    actor: str
    action: str
    entity_type: str
    entity_id: UUID
    summary: str
    metadata: dict = Field(default_factory=dict, validation_alias="metadata_")
    created_at: datetime
