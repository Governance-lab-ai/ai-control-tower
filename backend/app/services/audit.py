import csv
import io
import json
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_system import AISystem
from app.models.audit_event import AuditEvent
from app.models.evaluation import Evaluation
from app.models.human_review import HumanReview
from app.models.incident import Incident
from app.models.model_run import ModelRun
from app.models.prompt_version import PromptVersion


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


def export_audit_events(
    db: Session,
    *,
    system_id: UUID | None = None,
    department: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    risk_level: str | None = None,
    incident_type: str | None = None,
    limit: int = 1000,
) -> list[AuditEvent]:
    statement = select(AuditEvent)
    entity_ids = _filter_entity_ids(
        db,
        system_id=system_id,
        department=department,
        risk_level=risk_level,
        incident_type=incident_type,
    )
    if entity_ids is not None:
        if not entity_ids:
            return []
        statement = statement.where(AuditEvent.entity_id.in_(entity_ids))
    if start_date is not None:
        statement = statement.where(AuditEvent.created_at >= start_date)
    if end_date is not None:
        statement = statement.where(AuditEvent.created_at <= end_date)
    statement = statement.order_by(AuditEvent.created_at.desc()).limit(min(limit, 5000))
    return list(db.scalars(statement).all())


def audit_events_to_csv(events: list[AuditEvent]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["id", "created_at", "actor", "action", "entity_type", "entity_id", "summary", "metadata"],
    )
    writer.writeheader()
    for event in events:
        writer.writerow(
            {
                "id": str(event.id),
                "created_at": event.created_at.isoformat(),
                "actor": event.actor,
                "action": event.action,
                "entity_type": event.entity_type,
                "entity_id": str(event.entity_id),
                "summary": event.summary,
                "metadata": json.dumps(event.metadata_, sort_keys=True),
            }
        )
    return output.getvalue()


def get_audit_event(db: Session, event_id: UUID) -> AuditEvent:
    event = db.get(AuditEvent, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "AUDIT_EVENT_NOT_FOUND"})
    return event


def _filter_entity_ids(
    db: Session,
    *,
    system_id: UUID | None,
    department: str | None,
    risk_level: str | None,
    incident_type: str | None,
) -> set[UUID] | None:
    if system_id is None and department is None and risk_level is None and incident_type is None:
        return None

    system_statement = select(AISystem.id)
    if system_id is not None:
        system_statement = system_statement.where(AISystem.id == system_id)
    if department is not None:
        system_statement = system_statement.where(AISystem.department == department)
    if risk_level is not None:
        system_statement = system_statement.where(AISystem.risk_level == risk_level)
    system_ids = set(db.scalars(system_statement).all())

    if incident_type is not None and system_id is None and department is None and risk_level is None:
        incident_statement = select(Incident).where(Incident.incident_type == incident_type)
    else:
        incident_statement = select(Incident).where(Incident.ai_system_id.in_(system_ids))
        if incident_type is not None:
            incident_statement = incident_statement.where(Incident.incident_type == incident_type)
    incidents = list(db.scalars(incident_statement).all())

    if incident_type is not None and system_id is None and department is None and risk_level is None:
        system_ids.update(incident.ai_system_id for incident in incidents)

    model_run_ids = set(db.scalars(select(ModelRun.id).where(ModelRun.ai_system_id.in_(system_ids))).all()) if system_ids else set()
    prompt_version_ids = (
        set(db.scalars(select(PromptVersion.id).where(PromptVersion.ai_system_id.in_(system_ids))).all()) if system_ids else set()
    )
    evaluation_ids = (
        set(db.scalars(select(Evaluation.id).where(Evaluation.ai_system_id.in_(system_ids))).all()) if system_ids else set()
    )
    review_ids = set(db.scalars(select(HumanReview.id).where(HumanReview.ai_system_id.in_(system_ids))).all()) if system_ids else set()
    incident_ids = {incident.id for incident in incidents}

    return {
        *system_ids,
        *model_run_ids,
        *prompt_version_ids,
        *evaluation_ids,
        *review_ids,
        *incident_ids,
    }
