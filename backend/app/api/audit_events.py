from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.audit_event import AuditEventResponse
from app.services.audit import get_audit_event, list_audit_events

router = APIRouter(prefix="/audit-events", tags=["audit-events"])


@router.get("", response_model=list[AuditEventResponse])
def list_events(
    actor: str | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[AuditEventResponse]:
    return list_audit_events(
        db,
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
    )


@router.get("/{event_id}", response_model=AuditEventResponse)
def get_event(event_id: UUID, db: Session = Depends(get_db)) -> AuditEventResponse:
    return get_audit_event(db, event_id)
