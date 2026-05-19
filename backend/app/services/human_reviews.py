from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.ai_system import AISystem
from app.models.evaluation import Evaluation
from app.models.human_review import HumanReview
from app.models.model_run import ModelRun
from app.schemas.human_review import HumanReviewDecisionRequest
from app.services.audit import create_audit_event


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
            HumanReview.status == "pending",
        )
    )
    if existing is not None:
        return existing

    review = HumanReview(
        ai_system_id=ai_system.id,
        model_run_id=model_run_id,
        status="pending",
        reason=reason,
        priority=priority or _priority_for_system(ai_system),
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


def create_reviews_for_pii(
    db: Session,
    *,
    actor: str,
    ai_system: AISystem,
    model_run_id: UUID,
    input_pii_detected: bool,
    output_pii_detected: bool,
) -> list[HumanReview]:
    reviews: list[HumanReview] = []
    if input_pii_detected:
        reviews.append(
            create_review_if_needed(
                db,
                actor=actor,
                ai_system=ai_system,
                model_run_id=model_run_id,
                reason="pii_detected_input",
                summary="Input PII was detected. Reviewer should inspect the redacted evidence and decide whether the run can be used.",
                priority="high" if ai_system.risk_level in {"high", "critical"} else "medium",
            )
        )
    if output_pii_detected:
        reviews.append(
            create_review_if_needed(
                db,
                actor=actor,
                ai_system=ai_system,
                model_run_id=model_run_id,
                reason="pii_detected_output",
                summary="Output PII was detected. Reviewer should inspect the generated output before any downstream use.",
                priority="critical" if ai_system.risk_level in {"high", "critical"} else "high",
            )
        )
    return reviews


def create_review_for_high_risk_oversight(
    db: Session,
    *,
    actor: str,
    ai_system: AISystem,
    model_run_id: UUID,
) -> HumanReview | None:
    if ai_system.risk_level != "high" or not ai_system.human_oversight_required:
        return None
    return create_review_if_needed(
        db,
        actor=actor,
        ai_system=ai_system,
        model_run_id=model_run_id,
        reason="high_risk_human_oversight",
        summary="High-risk system requires human oversight for generated outputs.",
        priority="high",
    )


def create_review_for_evaluation(
    db: Session,
    *,
    actor: str,
    ai_system: AISystem,
    model_run: ModelRun,
    evaluation: Evaluation,
) -> HumanReview | None:
    if not evaluation.requires_human_review:
        return None
    reason = "hallucination_flag" if evaluation.hallucination_flag else "evaluation_below_threshold"
    summary = (
        f"Evaluation requires review. Score {evaluation.evaluation_score}/100, "
        f"threshold {evaluation.threshold}/100. {evaluation.evaluation_summary}"
    )
    return create_review_if_needed(
        db,
        actor=actor,
        ai_system=ai_system,
        model_run_id=model_run.id,
        reason=reason,
        summary=summary,
        priority="critical" if ai_system.risk_level == "critical" or evaluation.hallucination_flag else _priority_for_system(ai_system),
    )


def list_reviews(db: Session, *, status_filter: str | None = "pending") -> list[HumanReview]:
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
    if review.status != "pending":
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


def _priority_for_system(ai_system: AISystem) -> str:
    if ai_system.risk_level == "critical":
        return "critical"
    if ai_system.risk_level == "high":
        return "high"
    if ai_system.risk_level == "medium":
        return "medium"
    return "low"
