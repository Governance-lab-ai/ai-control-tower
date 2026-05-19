import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.ai_system import AISystem
from app.providers.llm import LLMRequest, get_llm_provider
from app.schemas.governance import GovernanceRunRequest, GovernanceRunResponse
from app.services.audit import create_audit_event


def run_governance_gateway(db: Session, settings: Settings, payload: GovernanceRunRequest) -> GovernanceRunResponse:
    system = db.get(AISystem, payload.ai_system_id)
    if system is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "AI_SYSTEM_NOT_FOUND"})

    if system.approval_status in {"blocked", "retired"}:
        response = GovernanceRunResponse(
            status="blocked",
            governance_messages=[
                f"Execution blocked because approval status is {system.approval_status}.",
                "No model provider call was made.",
            ],
        )
        _record_gateway_event(db, payload, system, response.status, response.governance_messages)
        db.commit()
        return response

    if system.approval_status == "pending":
        response = GovernanceRunResponse(
            status="requires_review",
            governance_messages=[
                "Execution requires review because the AI system approval status is pending.",
                "Pending systems are not executed in the local MVP gateway.",
            ],
        )
        _record_gateway_event(db, payload, system, response.status, response.governance_messages)
        db.commit()
        return response

    try:
        provider = get_llm_provider(settings.llm_provider)
        provider_response = provider.generate(
            LLMRequest(
                system_name=system.name,
                prompt=payload.prompt,
                input_text=payload.input_text,
                retrieved_documents=payload.retrieved_documents,
                metadata=payload.metadata,
            )
        )
    except Exception as exc:
        response = GovernanceRunResponse(
            status="failed",
            governance_messages=[
                "Gateway failed before completing model execution.",
                str(exc),
            ],
        )
        _record_gateway_event(db, payload, system, response.status, response.governance_messages)
        db.commit()
        return response

    run_id = uuid.uuid4()
    response = GovernanceRunResponse(
        run_id=run_id,
        status="executed",
        output_text=provider_response.output_text,
        governance_messages=[
            "AI system is approved for gateway execution.",
            f"Executed through provider {provider_response.provider} using model {provider_response.model}.",
            "Detailed model run persistence will be added in the model_runs episode.",
        ],
    )
    _record_gateway_event(db, payload, system, response.status, response.governance_messages, run_id=run_id)
    db.commit()
    return response


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
