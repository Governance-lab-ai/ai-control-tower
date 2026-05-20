from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.services.audit import create_audit_event
from app.services.pii import PIIResult


def create_pii_incident(
    db: Session,
    *,
    actor: str,
    ai_system_id: UUID,
    model_run_id: UUID,
    source: str,
    pii_result: PIIResult,
) -> Incident:
    severity = _severity_for_result(source, pii_result)
    incident = Incident(
        ai_system_id=ai_system_id,
        model_run_id=model_run_id,
        incident_type=f"pii_detected_{source}",
        severity=severity,
        title=f"PII detected in model {source}",
        description=_description(source, pii_result),
        status="open",
    )
    db.add(incident)
    db.flush()
    create_audit_event(
        db,
        actor=actor,
        action="incident.created",
        entity_type="incident",
        entity_id=incident.id,
        summary=incident.title,
        metadata={
            "ai_system_id": str(ai_system_id),
            "model_run_id": str(model_run_id),
            "incident_type": incident.incident_type,
            "severity": severity,
            "pii_types": pii_result.pii_types,
            "confidence": pii_result.confidence,
        },
    )
    return incident


def list_incidents(db: Session) -> list[Incident]:
    return list(db.scalars(select(Incident).order_by(Incident.created_at.desc())).all())


def list_incidents_for_system(db: Session, system_id: UUID) -> list[Incident]:
    statement = select(Incident).where(Incident.ai_system_id == system_id).order_by(Incident.created_at.desc())
    return list(db.scalars(statement).all())


def list_incidents_for_run(db: Session, run_id: UUID) -> list[Incident]:
    statement = select(Incident).where(Incident.model_run_id == run_id).order_by(Incident.created_at.desc())
    return list(db.scalars(statement).all())


def get_incident(db: Session, incident_id: UUID) -> Incident:
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "INCIDENT_NOT_FOUND"})
    return incident


def _description(source: str, pii_result: PIIResult) -> str:
    snippets = "; ".join(location.snippet for location in pii_result.locations[:3])
    return (
        f"Local regex PII detection found {', '.join(pii_result.pii_types)} in model {source}. "
        f"Confidence: {pii_result.confidence}. Redacted snippets: {snippets}"
    )


def _severity_for_result(source: str, pii_result: PIIResult) -> str:
    if source == "output":
        return "high" if pii_result.confidence == "high" else "medium"
    return "medium" if pii_result.confidence == "high" else "low"
