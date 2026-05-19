from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

IncidentStatus = Literal["open", "under_review", "resolved", "dismissed"]
IncidentSeverity = Literal["low", "medium", "high", "critical"]


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ai_system_id: UUID
    model_run_id: UUID | None
    incident_type: str
    severity: IncidentSeverity
    title: str
    description: str
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
