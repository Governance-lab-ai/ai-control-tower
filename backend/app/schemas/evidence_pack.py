from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel

from app.schemas.ai_system import AISystemResponse
from app.schemas.audit_event import AuditEventResponse
from app.schemas.human_review import HumanReviewResponse
from app.schemas.incident import IncidentResponse
from app.schemas.model_run import ModelRunResponse
from app.schemas.prompt_version import PromptVersionResponse


class EvidencePackResponse(BaseModel):
    generated_at: datetime
    evidence_pack_version: str
    run_id: UUID
    ai_system: AISystemResponse
    prompt_version: PromptVersionResponse | None
    model_run: ModelRunResponse
    incidents: list[IncidentResponse]
    human_reviews: list[HumanReviewResponse]
    audit_events: list[AuditEventResponse]


def evidence_generated_at() -> datetime:
    return datetime.now(timezone.utc)
