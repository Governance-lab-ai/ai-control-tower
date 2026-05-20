from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


def create_audit_event(
    db: Session,
    *,
    actor: str,
    action: str,
    entity_type: str,
    entity_id: UUID,
    summary: str,
    metadata: dict | None = None,
) -> AuditEvent:
    event = AuditEvent(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        summary=summary,
        metadata_=metadata or {},
    )
    db.add(event)
    return event


def list_audit_events(
    db: Session,
    *,
    actor: str | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    limit: int = 100,
) -> list[AuditEvent]:
    statement = select(AuditEvent)
    if actor:
        statement = statement.where(AuditEvent.actor == actor)
    if action:
        statement = statement.where(AuditEvent.action == action)
    if entity_type:
        statement = statement.where(AuditEvent.entity_type == entity_type)
    if entity_id:
        statement = statement.where(AuditEvent.entity_id == entity_id)
    statement = statement.order_by(AuditEvent.created_at.desc()).limit(min(limit, 500))
    return list(db.scalars(statement).all())


def get_audit_event(db: Session, event_id: UUID) -> AuditEvent:
    event = db.get(AuditEvent, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "AUDIT_EVENT_NOT_FOUND"})
    return event
