from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_system import AISystem
from app.models.audit_event import AuditEvent
from app.models.human_review import HumanReview
from app.models.incident import Incident
from app.models.model_run import ModelRun
from app.models.prompt_version import PromptVersion
from app.schemas.evidence_pack import EvidencePackResponse, evidence_generated_at
from app.services.model_runs import get_model_run


def get_model_run_evidence_pack(db: Session, run_id: UUID) -> EvidencePackResponse:
    model_run = get_model_run(db, run_id)
    ai_system = db.get(AISystem, model_run.ai_system_id)
    if ai_system is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "AI_SYSTEM_NOT_FOUND"})

    prompt_version = db.get(PromptVersion, model_run.prompt_version_id) if model_run.prompt_version_id else None
    incidents = _list_incidents(db, run_id)
    human_reviews = _list_reviews(db, run_id)
    audit_events = _list_related_audit_events(
        db,
        ai_system_id=ai_system.id,
        run=model_run,
        prompt_version=prompt_version,
        incidents=incidents,
        human_reviews=human_reviews,
    )

    return EvidencePackResponse(
        generated_at=evidence_generated_at(),
        evidence_pack_version="2026-05-local-v1",
        run_id=model_run.id,
        ai_system=ai_system,
        prompt_version=prompt_version,
        model_run=model_run,
        incidents=incidents,
        human_reviews=human_reviews,
        audit_events=audit_events,
    )


def _list_incidents(db: Session, run_id: UUID) -> list[Incident]:
    statement = select(Incident).where(Incident.model_run_id == run_id).order_by(Incident.created_at.asc())
    return list(db.scalars(statement).all())


def _list_reviews(db: Session, run_id: UUID) -> list[HumanReview]:
    statement = select(HumanReview).where(HumanReview.model_run_id == run_id).order_by(HumanReview.created_at.asc())
    return list(db.scalars(statement).all())


def _list_related_audit_events(
    db: Session,
    *,
    ai_system_id: UUID,
    run: ModelRun,
    prompt_version: PromptVersion | None,
    incidents: list[Incident],
    human_reviews: list[HumanReview],
) -> list[AuditEvent]:
    entity_ids = {
        ai_system_id,
        run.id,
        *(incident.id for incident in incidents),
        *(review.id for review in human_reviews),
    }
    if prompt_version is not None:
        entity_ids.add(prompt_version.id)

    statement = (
        select(AuditEvent)
        .where(AuditEvent.entity_id.in_(entity_ids))
        .order_by(AuditEvent.created_at.asc())
        .limit(500)
    )
    return list(db.scalars(statement).all())
