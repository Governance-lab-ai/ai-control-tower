from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings
from app.db.session import SessionLocal
from app.models.ai_system import AISystem
from app.models.evaluation import Evaluation
from app.models.model_run import ModelRun
from app.providers.evaluation import EvaluationRequest, EvaluationResult, get_evaluation_provider
from app.services.audit import create_audit_event
from app.services.model_runs import create_run_step
from app.services.review_policy import create_review_for_evaluation


def threshold_for_risk(settings: Settings, risk_level: str) -> int:
    thresholds = {
        "low": settings.evaluation_threshold_low,
        "medium": settings.evaluation_threshold_medium,
        "high": settings.evaluation_threshold_high,
        "critical": settings.evaluation_threshold_critical,
    }
    return thresholds.get(risk_level, settings.evaluation_threshold_medium)


def evaluate_model_run(
    db: Session,
    *,
    settings: Settings,
    ai_system: AISystem,
    model_run: ModelRun,
    retrieved_documents: list[str],
    actor: str,
) -> Evaluation:
    if model_run.output_text is None:
        raise ValueError("Cannot evaluate a model run without output text.")

    threshold = threshold_for_risk(settings, ai_system.risk_level)
    provider = get_evaluation_provider(settings.evaluation_provider, settings)
    result = provider.evaluate(
        EvaluationRequest(
            ai_system=ai_system,
            prompt=model_run.prompt,
            input_text=model_run.input_text,
            output_text=model_run.output_text,
            retrieved_documents=retrieved_documents,
            threshold=threshold,
        )
    )
    evaluation = create_evaluation(db, model_run=model_run, ai_system=ai_system, result=result)
    if evaluation.requires_human_review and model_run.status == "executed":
        model_run.status = "requires_review"

    create_audit_event(
        db,
        actor=actor,
        action="evaluation.created",
        entity_type="model_run",
        entity_id=model_run.id,
        summary=f"Evaluation created for model run {model_run.id}",
        metadata={
            "ai_system_id": str(ai_system.id),
            "evaluation_score": evaluation.evaluation_score,
            "relevance_score": evaluation.relevance_score,
            "groundedness_score": evaluation.groundedness_score,
            "hallucination_flag": evaluation.hallucination_flag,
            "requires_human_review": evaluation.requires_human_review,
            "threshold": evaluation.threshold,
        },
    )
    review = create_review_for_evaluation(db, actor=actor, ai_system=ai_system, model_run=model_run, evaluation=evaluation)
    create_run_step(
        db,
        model_run_id=model_run.id,
        step_type="evaluation",
        name="Output evaluation",
        status_="requires_review" if evaluation.requires_human_review else "passed",
        input_summary="Evaluation provider scored relevance, groundedness, and overall quality.",
        output_summary=evaluation.evaluation_summary,
        metadata={
            "provider": evaluation.provider,
            "evaluation_score": evaluation.evaluation_score,
            "relevance_score": evaluation.relevance_score,
            "groundedness_score": evaluation.groundedness_score,
            "hallucination_flag": evaluation.hallucination_flag,
            "requires_human_review": evaluation.requires_human_review,
            "threshold": evaluation.threshold,
            "review_created": review is not None,
        },
    )
    return evaluation


def evaluate_model_run_by_id(
    *,
    settings: Settings,
    ai_system_id: UUID,
    model_run_id: UUID,
    retrieved_documents: list[str],
    actor: str,
) -> None:
    with SessionLocal() as db:
        ai_system = db.get(AISystem, ai_system_id)
        model_run = db.get(ModelRun, model_run_id)
        if ai_system is None or model_run is None or model_run.output_text is None:
            return
        existing_evaluation = db.scalar(select(Evaluation).where(Evaluation.model_run_id == model_run_id))
        if existing_evaluation is not None:
            return
        evaluate_model_run(
            db,
            settings=settings,
            ai_system=ai_system,
            model_run=model_run,
            retrieved_documents=retrieved_documents,
            actor=actor,
        )
        db.commit()


def create_evaluation(db: Session, *, model_run: ModelRun, ai_system: AISystem, result: EvaluationResult) -> Evaluation:
    evaluation = Evaluation(
        model_run_id=model_run.id,
        ai_system_id=ai_system.id,
        provider=result.provider,
        evaluation_score=result.evaluation_score,
        relevance_score=result.relevance_score,
        groundedness_score=result.groundedness_score,
        hallucination_flag=result.hallucination_flag,
        evaluation_summary=result.evaluation_summary,
        requires_human_review=result.requires_human_review,
        threshold=result.threshold,
    )
    db.add(evaluation)
    db.flush()
    db.refresh(evaluation)
    return evaluation


def list_evaluations(db: Session, *, failed_only: bool = False) -> list[Evaluation]:
    statement = select(Evaluation).options(selectinload(Evaluation.model_run)).order_by(Evaluation.created_at.desc())
    if failed_only:
        statement = statement.where(Evaluation.requires_human_review.is_(True))
    return list(db.scalars(statement).all())


def get_evaluation(db: Session, evaluation_id: UUID) -> Evaluation:
    evaluation = db.get(Evaluation, evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "EVALUATION_NOT_FOUND"})
    return evaluation


def list_evaluations_for_system(db: Session, system_id: UUID, *, failed_only: bool = False) -> list[Evaluation]:
    system = db.get(AISystem, system_id)
    if system is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "AI_SYSTEM_NOT_FOUND"})
    statement = select(Evaluation).where(Evaluation.ai_system_id == system_id).order_by(Evaluation.created_at.desc())
    if failed_only:
        statement = statement.where(Evaluation.requires_human_review.is_(True))
    return list(db.scalars(statement).all())
