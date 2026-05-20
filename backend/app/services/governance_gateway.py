import uuid
from time import perf_counter

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.ai_system import AISystem
from app.providers.llm import LLMRequest, get_llm_provider
from app.schemas.governance import GovernanceRunRequest, GovernanceRunResponse
from app.services.audit import create_audit_event
from app.services.evaluations import evaluate_model_run_by_id
from app.services.incidents import create_pii_incident
from app.services.model_runs import create_model_run, create_run_step, estimate_local_cost_usd
from app.services.pii import PIIResult, get_pii_detector
from app.services.prompt_versions import get_active_prompt_version
from app.services.review_policy import create_review_for_high_risk_oversight, create_reviews_for_pii


def run_governance_gateway(
    db: Session,
    settings: Settings,
    payload: GovernanceRunRequest,
    background_tasks: BackgroundTasks | None = None,
) -> GovernanceRunResponse:
    system = db.get(AISystem, payload.ai_system_id)
    if system is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "AI_SYSTEM_NOT_FOUND"})

    active_prompt_version = get_active_prompt_version(db, system.id)
    pii_detector = get_pii_detector()
    input_pii_result = pii_detector.detect(payload.input_text)

    if system.approval_status in {"blocked", "retired"}:
        response = _record_non_executed_run(
            db,
            actor=payload.actor,
            payload=payload,
            system=system,
            prompt_version_id=active_prompt_version.id if active_prompt_version else None,
            gateway_status="blocked",
            input_pii_result=input_pii_result,
            governance_messages=[
                f"Execution blocked because approval status is {system.approval_status}.",
                "No model provider call was made.",
                "Blocked attempt was logged as a model run shell for audit review.",
            ],
        )
        return response

    if system.approval_status == "pending":
        response = _record_non_executed_run(
            db,
            actor=payload.actor,
            payload=payload,
            system=system,
            prompt_version_id=active_prompt_version.id if active_prompt_version else None,
            gateway_status="requires_review",
            input_pii_result=input_pii_result,
            governance_messages=[
                "Execution requires review because the AI system approval status is pending.",
                "Pending systems are not executed in the local MVP gateway.",
                "Review-required attempt was logged as a model run shell for audit review.",
            ],
        )
        return response

    provider_name = settings.llm_provider
    started_at = perf_counter()
    try:
        provider = get_llm_provider(settings.llm_provider, settings)
        provider_response = provider.generate(
            LLMRequest(
                system_name=system.name,
                prompt=payload.prompt,
                input_text=payload.input_text,
                retrieved_documents=payload.retrieved_documents,
                metadata=payload.metadata,
            )
        )
        latency_ms = max(1, round((perf_counter() - started_at) * 1000))
    except Exception as exc:
        latency_ms = max(1, round((perf_counter() - started_at) * 1000))
        run_id = _record_model_run_shell(
            db,
            payload,
            system,
            active_prompt_version.id if active_prompt_version else None,
            "failed",
            input_pii_result=input_pii_result,
            model_provider=provider_name,
            model_version="provider_failed",
            latency_ms=latency_ms,
        )
        _record_common_pre_execution_steps(
            db,
            model_run_id=run_id,
            system=system,
            input_pii_result=input_pii_result,
            approval_status="passed",
        )
        create_run_step(
            db,
            model_run_id=run_id,
            step_type="provider_call",
            name="LLM provider call",
            status_="failed",
            input_summary=f"Provider {provider_name} was selected behind the gateway.",
            output_summary="Provider call failed before a governed output was produced.",
            metadata={"provider": provider_name, "error": str(exc)},
            latency_ms=latency_ms,
        )
        response = GovernanceRunResponse(
            run_id=run_id,
            status="failed",
            governance_messages=[
                "Gateway failed before completing model execution.",
                "Failure was logged as a model run shell for audit review.",
                str(exc),
            ],
        )
        _record_gateway_event(db, payload, system, response.status, response.governance_messages, run_id=run_id)
        db.commit()
        return response

    output_pii_result = PIIResult(pii_detected=False, pii_types=[], locations=[], confidence="low")
    run_id = uuid.uuid4()
    output_pii_result = pii_detector.detect(provider_response.output_text)
    run_status = "requires_review" if input_pii_result.pii_detected or output_pii_result.pii_detected else "executed"
    cost_usd = estimate_local_cost_usd(
        payload.prompt,
        payload.input_text,
        provider_response.output_text,
        payload.retrieved_documents,
    )
    create_model_run(
        db,
        run_id=run_id,
        ai_system=system,
        prompt_version_id=active_prompt_version.id if active_prompt_version else None,
        prompt=payload.prompt,
        input_text=payload.input_text,
        output_text=provider_response.output_text,
        model_provider=provider_response.provider,
        model_name=provider_response.model,
        model_version=provider_response.model_version,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        status_=run_status,
        retrieved_documents=payload.retrieved_documents,
        input_pii_result=input_pii_result.to_dict(),
        output_pii_result=output_pii_result.to_dict(),
    )
    _record_common_pre_execution_steps(
        db,
        model_run_id=run_id,
        system=system,
        input_pii_result=input_pii_result,
        approval_status="passed",
    )
    create_run_step(
        db,
        model_run_id=run_id,
        step_type="provider_call",
        name="LLM provider call",
        status_="completed",
        input_summary=f"Provider {provider_response.provider} received the governed prompt and input.",
        output_summary=f"Provider returned output through model {provider_response.model}.",
        metadata={
            "provider": provider_response.provider,
            "model": provider_response.model,
            "model_version": provider_response.model_version,
            "estimated_cost_usd": cost_usd,
        },
        latency_ms=latency_ms,
    )
    _record_output_pii_step(db, model_run_id=run_id, output_pii_result=output_pii_result)
    _record_pii_side_effects(
        db,
        actor=payload.actor,
        ai_system=system,
        model_run_id=run_id,
        input_pii_result=input_pii_result,
        output_pii_result=output_pii_result,
    )
    high_risk_review = create_review_for_high_risk_oversight(db, actor=payload.actor, ai_system=system, model_run_id=run_id)
    _record_review_routing_step(
        db,
        model_run_id=run_id,
        input_pii_result=input_pii_result,
        output_pii_result=output_pii_result,
        high_risk_review_created=high_risk_review is not None,
    )

    if background_tasks is not None:
        background_tasks.add_task(
            evaluate_model_run_by_id,
            settings=settings,
            ai_system_id=system.id,
            model_run_id=run_id,
            retrieved_documents=payload.retrieved_documents,
            actor=payload.actor,
        )

    gateway_status = "requires_review" if run_status == "requires_review" else "executed"
    response = GovernanceRunResponse(
        run_id=run_id,
        status=gateway_status,
        output_text=provider_response.output_text,
        governance_messages=[
            "AI system is approved for gateway execution.",
            f"Linked active prompt version {active_prompt_version.version}." if active_prompt_version else "No active prompt version was linked.",
            f"Executed through provider {provider_response.provider} using model {provider_response.model}.",
            f"Model run logged with latency {latency_ms}ms and estimated cost ${cost_usd:.6f}.",
            "Evaluation queued for asynchronous local processing.",
            *_pii_messages("input", input_pii_result),
            *_pii_messages("output", output_pii_result),
        ],
    )
    _record_gateway_event(db, payload, system, response.status, response.governance_messages, run_id=run_id)
    db.commit()
    return response


def _record_non_executed_run(
    db: Session,
    actor: str,
    payload: GovernanceRunRequest,
    system: AISystem,
    prompt_version_id: uuid.UUID | None,
    gateway_status: str,
    input_pii_result: PIIResult,
    governance_messages: list[str],
) -> GovernanceRunResponse:
    run_id = _record_model_run_shell(
        db,
        payload,
        system,
        prompt_version_id,
        gateway_status,
        input_pii_result=input_pii_result,
    )
    _record_common_pre_execution_steps(
        db,
        model_run_id=run_id,
        system=system,
        input_pii_result=input_pii_result,
        approval_status=gateway_status,
    )
    _record_pii_side_effects(
        db,
        actor=actor,
        ai_system=system,
        model_run_id=run_id,
        input_pii_result=input_pii_result,
        output_pii_result=None,
    )
    response = GovernanceRunResponse(
        run_id=run_id,
        status=gateway_status,
        governance_messages=[
            *governance_messages,
            *_pii_messages("input", input_pii_result),
        ],
    )
    _record_gateway_event(db, payload, system, response.status, response.governance_messages, run_id=run_id)
    _record_review_routing_step(
        db,
        model_run_id=run_id,
        input_pii_result=input_pii_result,
        output_pii_result=None,
        high_risk_review_created=False,
    )
    db.commit()
    return response


def _record_model_run_shell(
    db: Session,
    payload: GovernanceRunRequest,
    system: AISystem,
    prompt_version_id: uuid.UUID | None,
    gateway_status: str,
    input_pii_result: PIIResult | None = None,
    model_provider: str | None = None,
    model_version: str = "not_executed",
    latency_ms: int = 0,
) -> uuid.UUID:
    run_id = uuid.uuid4()
    create_model_run(
        db,
        run_id=run_id,
        ai_system=system,
        prompt_version_id=prompt_version_id,
        prompt=payload.prompt,
        input_text=payload.input_text,
        output_text=None,
        model_provider=model_provider or system.model_provider,
        model_name=system.model_name,
        model_version=model_version,
        latency_ms=latency_ms,
        cost_usd=0,
        status_=gateway_status,
        retrieved_documents=payload.retrieved_documents,
        input_pii_result=input_pii_result.to_dict() if input_pii_result else None,
    )
    return run_id


def _record_common_pre_execution_steps(
    db: Session,
    *,
    model_run_id: uuid.UUID,
    system: AISystem,
    input_pii_result: PIIResult,
    approval_status: str,
) -> None:
    approval_output_by_status = {
        "passed": "AI system approval check passed; provider call was allowed.",
        "blocked": f"Provider call blocked because approval status is {system.approval_status}.",
        "requires_review": "Provider call held because pending systems require review before execution.",
        "failed": "Approval check passed, but a later gateway step failed.",
    }
    create_run_step(
        db,
        model_run_id=model_run_id,
        step_type="approval_check",
        name="AI system approval check",
        status_=approval_status,
        input_summary=f"Approval status: {system.approval_status}; risk level: {system.risk_level}.",
        output_summary=approval_output_by_status.get(approval_status, "Approval check completed."),
        metadata={
            "ai_system_id": str(system.id),
            "approval_status": system.approval_status,
            "risk_level": system.risk_level,
            "human_oversight_required": system.human_oversight_required,
        },
    )
    create_run_step(
        db,
        model_run_id=model_run_id,
        step_type="pii_check",
        name="Input PII check",
        status_="requires_review" if input_pii_result.pii_detected else "passed",
        input_summary="Input text was scanned by the configured local PII detector.",
        output_summary=_pii_step_summary("input", input_pii_result),
        metadata=_pii_step_metadata(input_pii_result),
    )


def _record_output_pii_step(db: Session, *, model_run_id: uuid.UUID, output_pii_result: PIIResult) -> None:
    create_run_step(
        db,
        model_run_id=model_run_id,
        step_type="pii_check",
        name="Output PII check",
        status_="requires_review" if output_pii_result.pii_detected else "passed",
        input_summary="Provider output was scanned before it was returned to the caller.",
        output_summary=_pii_step_summary("output", output_pii_result),
        metadata=_pii_step_metadata(output_pii_result),
    )


def _record_review_routing_step(
    db: Session,
    *,
    model_run_id: uuid.UUID,
    input_pii_result: PIIResult,
    output_pii_result: PIIResult | None,
    high_risk_review_created: bool,
) -> None:
    reasons: list[str] = []
    if input_pii_result.pii_detected:
        reasons.append("input_pii")
    if output_pii_result and output_pii_result.pii_detected:
        reasons.append("output_pii")
    if high_risk_review_created:
        reasons.append("high_risk_human_oversight")
    create_run_step(
        db,
        model_run_id=model_run_id,
        step_type="review_routing",
        name="Human review routing",
        status_="created" if reasons else "skipped",
        input_summary="Gateway review rules evaluated the run signals.",
        output_summary="Review item created." if reasons else "No review item was required by immediate gateway signals.",
        metadata={"reasons": reasons},
    )


def _pii_step_summary(source: str, result: PIIResult) -> str:
    if not result.pii_detected:
        return f"No PII detected in {source}."
    return f"PII detected in {source}: {', '.join(result.pii_types)}; confidence {result.confidence}."


def _pii_step_metadata(result: PIIResult) -> dict:
    return result.to_dict()


def _record_pii_side_effects(
    db: Session,
    *,
    actor: str,
    ai_system: AISystem,
    model_run_id: uuid.UUID,
    input_pii_result: PIIResult,
    output_pii_result: PIIResult | None,
) -> None:
    if input_pii_result.pii_detected:
        create_pii_incident(db, actor=actor, ai_system_id=ai_system.id, model_run_id=model_run_id, source="input", pii_result=input_pii_result)
    output_pii_detected = output_pii_result.pii_detected if output_pii_result else False
    if output_pii_result and output_pii_result.pii_detected:
        create_pii_incident(db, actor=actor, ai_system_id=ai_system.id, model_run_id=model_run_id, source="output", pii_result=output_pii_result)
    create_reviews_for_pii(
        db,
        actor=actor,
        ai_system=ai_system,
        model_run_id=model_run_id,
        input_pii_detected=input_pii_result.pii_detected,
        output_pii_detected=output_pii_detected,
    )


def _pii_messages(source: str, result: PIIResult) -> list[str]:
    if not result.pii_detected:
        return []
    return [
        f"PII detected in {source}: {', '.join(result.pii_types)}.",
        f"Created PII incident with {result.confidence} confidence and redacted snippets.",
    ]


def _record_gateway_event(
    db: Session,
    payload: GovernanceRunRequest,
    system: AISystem,
    gateway_status: str,
    governance_messages: list[str],
    run_id: uuid.UUID | None = None,
) -> None:
    action_by_status = {
        "executed": "governance.run.executed",
        "blocked": "governance.run.blocked",
        "requires_review": "governance.run.requires_review",
        "failed": "governance.run.failed",
    }
    create_audit_event(
        db,
        actor=payload.actor,
        action=action_by_status[gateway_status],
        entity_type="ai_system",
        entity_id=system.id,
        summary=f"Governance gateway run {gateway_status} for {system.name}",
        metadata={
            "gateway_status": gateway_status,
            "approval_status": system.approval_status,
            "run_id": str(run_id) if run_id else None,
            "metadata": payload.metadata,
            "retrieved_document_count": len(payload.retrieved_documents),
            "governance_messages": governance_messages,
        },
    )
