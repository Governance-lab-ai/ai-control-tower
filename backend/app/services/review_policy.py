from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ai_system import AISystem
from app.models.evaluation import Evaluation
from app.models.human_review import HumanReview
from app.models.model_run import ModelRun
from app.services.human_reviews import create_review_if_needed
from app.services.review_constants import (
    REVIEW_PRIORITY_CRITICAL,
    REVIEW_PRIORITY_HIGH,
    REVIEW_PRIORITY_MEDIUM,
    REVIEW_REASON_EVALUATION_BELOW_THRESHOLD,
    REVIEW_REASON_HALLUCINATION_FLAG,
    REVIEW_REASON_HIGH_RISK_HUMAN_OVERSIGHT,
    REVIEW_REASON_PII_INPUT,
    REVIEW_REASON_PII_OUTPUT,
    priority_for_system,
)


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
                reason=REVIEW_REASON_PII_INPUT,
                summary="Input PII was detected. Reviewer should inspect the redacted evidence and decide whether the run can be used.",
                priority=REVIEW_PRIORITY_HIGH if ai_system.risk_level in {"high", "critical"} else REVIEW_PRIORITY_MEDIUM,
            )
        )
    if output_pii_detected:
        reviews.append(
            create_review_if_needed(
                db,
                actor=actor,
                ai_system=ai_system,
                model_run_id=model_run_id,
                reason=REVIEW_REASON_PII_OUTPUT,
                summary="Output PII was detected. Reviewer should inspect the generated output before any downstream use.",
                priority=REVIEW_PRIORITY_CRITICAL if ai_system.risk_level in {"high", "critical"} else REVIEW_PRIORITY_HIGH,
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
        reason=REVIEW_REASON_HIGH_RISK_HUMAN_OVERSIGHT,
        summary="High-risk system requires human oversight for generated outputs.",
        priority=REVIEW_PRIORITY_HIGH,
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
    reason = REVIEW_REASON_HALLUCINATION_FLAG if evaluation.hallucination_flag else REVIEW_REASON_EVALUATION_BELOW_THRESHOLD
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
        priority=REVIEW_PRIORITY_CRITICAL if ai_system.risk_level == "critical" or evaluation.hallucination_flag else priority_for_system(ai_system),
    )
