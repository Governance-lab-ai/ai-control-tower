from uuid import UUID

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
