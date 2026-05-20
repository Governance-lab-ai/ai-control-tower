from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.ai_system import AISystem
from app.models.model_run import ModelRun, RetrievedDocument, RunStep


def estimate_local_cost_usd(prompt: str, input_text: str, output_text: str, retrieved_documents: list[str]) -> float:
    character_count = len(prompt) + len(input_text) + len(output_text) + sum(len(document) for document in retrieved_documents)
    estimated_tokens = max(1, character_count // 4)
    return round(estimated_tokens * 0.000001, 6)


def create_model_run(
    db: Session,
    *,
    run_id: UUID | None = None,
    ai_system: AISystem,
    prompt_version_id: UUID | None,
    prompt: str,
    input_text: str,
    output_text: str | None,
    model_provider: str,
    model_name: str,
    model_version: str,
    latency_ms: int,
    cost_usd: float,
    status_: str,
    retrieved_documents: list[str],
    input_pii_result: dict | None = None,
    output_pii_result: dict | None = None,
) -> ModelRun:
    model_run = ModelRun(
        id=run_id or uuid4(),
        ai_system_id=ai_system.id,
        prompt_version_id=prompt_version_id,
        prompt=prompt,
        input_text=input_text,
        output_text=output_text,
        model_provider=model_provider,
        model_name=model_name,
        model_version=model_version,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        status=status_,
        input_pii_result=input_pii_result or {},
        output_pii_result=output_pii_result or {},
    )
    db.add(model_run)
    db.flush()

    for index, document in enumerate(retrieved_documents, start=1):
        db.add(
            RetrievedDocument(
                model_run_id=model_run.id,
                source_label=f"retrieved_document_{index}",
                content=document,
                ordinal=index,
            )
        )

    db.flush()
    db.refresh(model_run, attribute_names=["retrieved_documents"])
    return model_run


def create_run_step(
    db: Session,
    *,
    model_run_id: UUID,
    step_type: str,
    name: str,
    status_: str,
    input_summary: str | None = None,
    output_summary: str | None = None,
    metadata: dict | None = None,
    latency_ms: int | None = None,
) -> RunStep:
    run_step = RunStep(
        model_run_id=model_run_id,
        step_type=step_type,
        name=name,
        status=status_,
        input_summary=input_summary,
        output_summary=output_summary,
        metadata_=metadata or {},
        latency_ms=latency_ms,
    )
    db.add(run_step)
    db.flush()
    return run_step


def _model_run_load_options():
    return (
        selectinload(ModelRun.retrieved_documents),
        selectinload(ModelRun.evaluation),
        selectinload(ModelRun.run_steps),
    )


def list_model_runs(db: Session) -> list[ModelRun]:
    statement = (
        select(ModelRun)
        .options(*_model_run_load_options())
        .order_by(ModelRun.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_model_run(db: Session, run_id: UUID) -> ModelRun:
    statement = (
        select(ModelRun)
        .options(*_model_run_load_options())
        .where(ModelRun.id == run_id)
    )
    model_run = db.scalars(statement).first()
    if model_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "MODEL_RUN_NOT_FOUND"})
    return model_run


def list_model_runs_for_system(db: Session, system_id: UUID) -> list[ModelRun]:
    system = db.get(AISystem, system_id)
    if system is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "AI_SYSTEM_NOT_FOUND"})

    statement = (
        select(ModelRun)
        .options(*_model_run_load_options())
        .where(ModelRun.ai_system_id == system_id)
        .order_by(ModelRun.created_at.desc())
    )
    return list(db.scalars(statement).all())
