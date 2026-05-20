from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.ai_system import AISystem
from app.models.human_review import HumanReview
from app.models.model_run import ModelRun
from app.schemas.human_review import HumanReviewDecisionRequest
from app.services.audit import create_audit_event
from app.services.review_constants import REVIEW_STATUS_PENDING, priority_for_system


def create_review_if_needed(
    db: Session,
    *,
    actor: str,
    ai_system: AISystem,
    model_run_id: UUID,
    reason: str,
    summary: str,
    priority: str | None = None,
) -> HumanReview:
    existing = db.scalar(
        select(HumanReview).where(
            HumanReview.model_run_id == model_run_id,
            HumanReview.reason == reason,
            HumanReview.status == REVIEW_STATUS_PENDING,
        )
    )
    if existing is not None:
        return existing

    review = HumanReview(
        ai_system_id=ai_system.id,
        model_run_id=model_run_id,
        status=REVIEW_STATUS_PENDING,
        reason=reason,
        priority=priority or priority_for_system(ai_system),
        summary=summary,
    )
    db.add(review)
    db.flush()
    create_audit_event(
        db,
        actor=actor,
        action="human_review.created",
        entity_type="human_review",
        entity_id=review.id,
        summary=f"Human review queued for {ai_system.name}",
        metadata={
            "ai_system_id": str(ai_system.id),
            "model_run_id": str(model_run_id),
            "reason": reason,
            "priority": review.priority,
        },
    )
    return review


def list_reviews(db: Session, *, status_filter: str | None = REVIEW_STATUS_PENDING) -> list[HumanReview]:
    statement = select(HumanReview).order_by(HumanReview.created_at.desc())
    if status_filter:
        statement = statement.where(HumanReview.status == status_filter)
    return list(db.scalars(statement).all())


def get_review(db: Session, review_id: UUID) -> HumanReview:
    statement = (
        select(HumanReview)
        .options(
            selectinload(HumanReview.model_run).selectinload(ModelRun.retrieved_documents),
            selectinload(HumanReview.model_run).selectinload(ModelRun.evaluation),
        )
        .where(HumanReview.id == review_id)
    )
    review = db.scalars(statement).first()
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "HUMAN_REVIEW_NOT_FOUND"})
    return review


def decide_review(db: Session, *, review_id: UUID, payload: HumanReviewDecisionRequest) -> HumanReview:
    review = get_review(db, review_id)
    if review.status != REVIEW_STATUS_PENDING:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "HUMAN_REVIEW_ALREADY_DECIDED"})

    review.status = payload.decision
    review.reviewer_id = payload.reviewer_id
    review.reviewer_name = payload.reviewer_name
    review.decision_notes = payload.notes
    review.decided_at = datetime.now(timezone.utc)
    review.updated_at = review.decided_at

    if review.model_run and payload.decision in {"rejected", "escalated"}:
        review.model_run.status = "requires_review"

    create_audit_event(
        db,
        actor=payload.reviewer_id,
        action=f"human_review.{payload.decision}",
        entity_type="human_review",
        entity_id=review.id,
        summary=f"Human review {payload.decision} by {payload.reviewer_name}",
        metadata={
            "ai_system_id": str(review.ai_system_id),
            "model_run_id": str(review.model_run_id),
            "reviewer_id": payload.reviewer_id,
            "reviewer_name": payload.reviewer_name,
            "decision": payload.decision,
            "notes": payload.notes,
            "decided_at": review.decided_at.isoformat(),
        },
    )
    db.commit()
    db.refresh(review)
    return review
