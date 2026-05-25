from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.ai_system import AISystem
from app.models.audit_event import AuditEvent
from app.models.evaluation import Evaluation
from app.models.human_review import HumanReview
from app.models.incident import Incident
from app.models.model_run import ModelRun, RetrievedDocument, RunStep
from app.models.prompt_version import PromptVersion
from app.schemas.ai_system import AISystemCreate
from app.schemas.prompt_version import PromptVersionCreate
from app.services.ai_systems import create_ai_system
from app.services.evaluations import evaluate_model_run
from app.services.human_reviews import create_review_if_needed
from app.services.incidents import create_pii_incident
from app.services.model_runs import create_model_run, create_run_step, estimate_local_cost_usd
from app.services.pii import get_pii_detector
from app.services.prompt_versions import activate_prompt_version, create_prompt_version, ensure_default_prompt_version, get_active_prompt_version
from app.services.review_constants import REVIEW_PRIORITY_HIGH, REVIEW_PRIORITY_MEDIUM, REVIEW_REASON_PII_INPUT, REVIEW_REASON_PII_OUTPUT


SHOWCASE_PROMPTS = {
    "Customer Support Summariser": (
        "You are the approved Customer Support Summariser. Summarise the customer issue, identify policy-relevant facts, "
        "avoid exposing unnecessary personal data, and recommend whether a human support reviewer should inspect the response."
    ),
    "Sales Email Generator": (
        "You are the approved Sales Email Generator. Draft concise outbound copy from approved product messaging only. "
        "Do not invent claims, pricing, customer names, or guarantees."
    ),
    "HR CV Screening Assistant": (
        "You are the blocked HR CV Screening Assistant. Do not make hiring recommendations. Explain that high-risk HR use requires governance review."
    ),
    "Procurement Policy Assistant": (
        "You are the approved Procurement Policy Assistant. Answer only from retrieved procurement policy context and highlight any missing evidence."
    ),
}

DEMO_SYSTEM_NAMES = tuple(SHOWCASE_PROMPTS)


def _showcase_systems(settings: Settings) -> tuple[AISystemCreate, ...]:
    provider = "ollama" if settings.llm_provider == "ollama" else "mock"
    model_name = settings.ollama_model if settings.llm_provider == "ollama" else "mock-governance-gateway"
    return (
        AISystemCreate(
            name="Customer Support Summariser",
            description="Summarises support tickets, checks retrieved support policy, and routes risky cases to review.",
            department="Customer Operations",
            owner_name="Avery Stone",
            owner_email="avery.stone@example.test",
            model_provider=provider,
            model_name=model_name,
            data_sources=["support_tickets", "refund_policy", "shipping_policy"],
            contains_personal_data=True,
            risk_level="medium",
            human_oversight_required=True,
            approval_status="approved",
        ),
        AISystemCreate(
            name="Sales Email Generator",
            description="Drafts sales outreach from approved messaging while avoiding unsupported claims.",
            department="Revenue",
            owner_name="Morgan Vale",
            owner_email="morgan.vale@example.test",
            model_provider=provider,
            model_name=model_name,
            data_sources=["approved_product_messaging"],
            contains_personal_data=False,
            risk_level="low",
            human_oversight_required=False,
            approval_status="approved",
        ),
        AISystemCreate(
            name="HR CV Screening Assistant",
            description="High-risk HR screening concept kept blocked to demonstrate approval controls.",
            department="People",
            owner_name="Jordan Reid",
            owner_email="jordan.reid@example.test",
            model_provider=provider,
            model_name=model_name,
            data_sources=["candidate_profiles", "role_requirements"],
            contains_personal_data=True,
            risk_level="high",
            human_oversight_required=True,
            approval_status="blocked",
        ),
        AISystemCreate(
            name="Procurement Policy Assistant",
            description="Answers internal procurement questions using approved policy excerpts and source grounding.",
            department="Procurement",
            owner_name="Sam Rivera",
            owner_email="sam.rivera@example.test",
            model_provider=provider,
            model_name=model_name,
            data_sources=["procurement_policy", "vendor_risk_policy"],
            contains_personal_data=False,
            risk_level="medium",
            human_oversight_required=True,
            approval_status="approved",
        ),
    )

def seed_demo_systems(db: Session) -> int:
    settings = get_settings()
    existing_names = set(db.scalars(select(AISystem.name)).all())
    created = 0
    for payload in _showcase_systems(settings):
        if payload.name in existing_names:
            continue
        create_ai_system(db, payload)
        created += 1
    ensure_showcase_prompt_versions(db)
    ensure_default_prompt_versions(db)
    seed_demo_model_runs(db)
    seed_demo_evaluations(db)
    return created


def clear_demo_data(db: Session) -> dict[str, int]:
    demo_system_ids = list(db.scalars(select(AISystem.id).where(AISystem.name.in_(DEMO_SYSTEM_NAMES))).all())
    if not demo_system_ids:
        return {
            "ai_systems": 0,
            "model_runs": 0,
            "retrieved_documents": 0,
            "run_steps": 0,
            "evaluations": 0,
            "human_reviews": 0,
            "incidents": 0,
            "prompt_versions": 0,
            "audit_events": 0,
        }

    model_run_ids = list(db.scalars(select(ModelRun.id).where(ModelRun.ai_system_id.in_(demo_system_ids))).all())
    prompt_version_ids = list(db.scalars(select(PromptVersion.id).where(PromptVersion.ai_system_id.in_(demo_system_ids))).all())
    review_ids = list(db.scalars(select(HumanReview.id).where(HumanReview.ai_system_id.in_(demo_system_ids))).all())
    incident_ids = list(db.scalars(select(Incident.id).where(Incident.ai_system_id.in_(demo_system_ids))).all())
    evaluation_ids = list(db.scalars(select(Evaluation.id).where(Evaluation.ai_system_id.in_(demo_system_ids))).all())

    counts = {
        "run_steps": _delete_where(db, RunStep, RunStep.model_run_id.in_(model_run_ids)) if model_run_ids else 0,
        "retrieved_documents": _delete_where(db, RetrievedDocument, RetrievedDocument.model_run_id.in_(model_run_ids)) if model_run_ids else 0,
        "evaluations": _delete_where(db, Evaluation, Evaluation.ai_system_id.in_(demo_system_ids)),
        "human_reviews": _delete_where(db, HumanReview, HumanReview.ai_system_id.in_(demo_system_ids)),
        "incidents": _delete_where(db, Incident, Incident.ai_system_id.in_(demo_system_ids)),
        "model_runs": _delete_where(db, ModelRun, ModelRun.ai_system_id.in_(demo_system_ids)),
        "prompt_versions": _delete_where(db, PromptVersion, PromptVersion.ai_system_id.in_(demo_system_ids)),
    }
    audit_entity_ids = [*demo_system_ids, *model_run_ids, *prompt_version_ids, *review_ids, *incident_ids, *evaluation_ids]
    counts["audit_events"] = _delete_where(db, AuditEvent, AuditEvent.entity_id.in_(audit_entity_ids)) if audit_entity_ids else 0
    counts["ai_systems"] = _delete_where(db, AISystem, AISystem.id.in_(demo_system_ids))
    db.commit()
    return counts


def clear_all_application_data(db: Session) -> dict[str, int]:
    counts = {
        "run_steps": _delete_all(db, RunStep),
        "retrieved_documents": _delete_all(db, RetrievedDocument),
        "evaluations": _delete_all(db, Evaluation),
        "human_reviews": _delete_all(db, HumanReview),
        "incidents": _delete_all(db, Incident),
        "model_runs": _delete_all(db, ModelRun),
        "prompt_versions": _delete_all(db, PromptVersion),
        "audit_events": _delete_all(db, AuditEvent),
        "ai_systems": _delete_all(db, AISystem),
    }
    db.commit()
    return counts


def _delete_where(db: Session, model: type, where_clause) -> int:
    result = db.execute(delete(model).where(where_clause))
    return int(result.rowcount or 0)


def _delete_all(db: Session, model: type) -> int:
    result = db.execute(delete(model))
    return int(result.rowcount or 0)


def ensure_default_prompt_versions(db: Session) -> int:
    created = 0
    systems = db.scalars(select(AISystem)).all()
    for system in systems:
        if get_active_prompt_version(db, system.id) is not None:
            continue
        ensure_default_prompt_version(db, system)
        created += 1
    if created:
        db.commit()
    return created


def ensure_showcase_prompt_versions(db: Session) -> int:
    created = 0
    systems_by_name = {system.name: system for system in db.scalars(select(AISystem).where(AISystem.name.in_(DEMO_SYSTEM_NAMES))).all()}
    for system_name, prompt_text in SHOWCASE_PROMPTS.items():
        system = systems_by_name.get(system_name)
        if system is None:
            continue
        existing_showcase_prompt = db.scalar(
            select(PromptVersion).where(
                PromptVersion.ai_system_id == system.id,
                PromptVersion.name == "Approved showcase prompt",
            )
        )
        if existing_showcase_prompt is not None:
            if existing_showcase_prompt.status != "active":
                activate_prompt_version(db, existing_showcase_prompt.id)
            continue
        create_prompt_version(
            db,
            system.id,
            PromptVersionCreate(
                version="v2",
                name="Approved showcase prompt",
                prompt_text=prompt_text,
                status="active",
            ),
        )
        created += 1
    return created


def seed_demo_model_runs(db: Session) -> int:
    showcase_system_ids = list(db.scalars(select(AISystem.id).where(AISystem.name.in_(DEMO_SYSTEM_NAMES))).all())
    if not showcase_system_ids:
        return 0
    existing_run_count = db.scalar(select(ModelRun.id).where(ModelRun.ai_system_id.in_(showcase_system_ids)).limit(1))
    if existing_run_count is not None:
        return 0

    systems_by_name = {system.name: system for system in db.scalars(select(AISystem)).all()}
    pii_detector = get_pii_detector()
    created = 0
    demo_runs = [
        {
            "system_name": "Customer Support Summariser",
            "input_text": "Customer name: Alex Morgan. Email: alex.morgan@example.test. Ticket says order 7841 arrived damaged and the customer wants refund options.",
            "output_text": "The customer reports a damaged order and asks about refund options. Use the damaged shipment policy and route to a support reviewer because personal data is present.",
            "retrieved_documents": [
                "Refund policy: damaged shipments are eligible for replacement or refund after support verification.",
                "Support handling rule: redact unnecessary personal data before sharing summaries downstream.",
            ],
            "latency_ms": 118,
            "status": "requires_review",
            "review_reason": REVIEW_REASON_PII_INPUT,
            "review_priority": REVIEW_PRIORITY_HIGH,
        },
        {
            "system_name": "Customer Support Summariser",
            "input_text": "Synthetic support ticket asks whether a delayed order can be refunded after five business days.",
            "output_text": "The ticket concerns a delayed order. The retrieved policy says refund eligibility starts after five business days, so the next step is to verify shipment status before offering options.",
            "retrieved_documents": [
                "Shipping policy: delayed orders become refund eligible after five business days without carrier movement.",
                "Support policy: provide status summary and next action, not compensation guarantees.",
            ],
            "latency_ms": 96,
            "status": "executed",
        },
        {
            "system_name": "Sales Email Generator",
            "input_text": "Draft a concise opening email for risk leaders evaluating AI governance controls.",
            "output_text": "Subject: Bring control to AI workflows\n\nHi there, your teams can route AI usage through a governed gateway that records approvals, model runs, evaluations, and review decisions.",
            "retrieved_documents": ["Approved product messaging: governance gateway, registry, audit trail, and human review queue."],
            "latency_ms": 63,
            "status": "executed",
        },
        {
            "system_name": "Procurement Policy Assistant",
            "input_text": "Can a team approve a new analytics vendor if security review is still pending?",
            "output_text": "No. The retrieved procurement policy requires vendor risk review completion before approval. The team can collect business justification while security review is pending.",
            "retrieved_documents": [
                "Procurement policy: vendors processing internal data require completed security review before approval.",
                "Vendor risk policy: business justification may be prepared before security sign-off but cannot replace it.",
            ],
            "latency_ms": 74,
            "status": "executed",
        },
    ]

    for item in demo_runs:
        system = systems_by_name.get(item["system_name"])
        if system is None:
            continue
        prompt_version = get_active_prompt_version(db, system.id)
        prompt_text = prompt_version.prompt_text if prompt_version else SHOWCASE_PROMPTS[item["system_name"]]
        input_pii_result = pii_detector.detect(item["input_text"])
        output_pii_result = pii_detector.detect(item["output_text"])
        model_run = create_model_run(
            db,
            ai_system=system,
            prompt_version_id=prompt_version.id if prompt_version else None,
            prompt=prompt_text,
            input_text=item["input_text"],
            output_text=item["output_text"],
            model_provider="seed_showcase",
            model_name=system.model_name,
            model_version="seed-demo-v1",
            latency_ms=item["latency_ms"],
            cost_usd=estimate_local_cost_usd(prompt_text, item["input_text"], item["output_text"], item["retrieved_documents"]),
            status_=item["status"],
            retrieved_documents=item["retrieved_documents"],
            input_pii_result=input_pii_result.to_dict(),
            output_pii_result=output_pii_result.to_dict(),
        )
        _seed_run_steps(
            db,
            model_run=model_run,
            system=system,
            input_pii_result=input_pii_result.to_dict(),
            output_pii_result=output_pii_result.to_dict(),
        )
        if input_pii_result.pii_detected:
            create_pii_incident(db, actor="seed:showcase", ai_system_id=system.id, model_run_id=model_run.id, source="input", pii_result=input_pii_result)
            create_review_if_needed(
                db,
                actor="seed:showcase",
                ai_system=system,
                model_run_id=model_run.id,
                reason=item.get("review_reason", REVIEW_REASON_PII_INPUT),
                summary="Seeded showcase review: input PII was detected and should be inspected before downstream use.",
                priority=item.get("review_priority", REVIEW_PRIORITY_MEDIUM),
            )
        if output_pii_result.pii_detected:
            create_pii_incident(db, actor="seed:showcase", ai_system_id=system.id, model_run_id=model_run.id, source="output", pii_result=output_pii_result)
            create_review_if_needed(
                db,
                actor="seed:showcase",
                ai_system=system,
                model_run_id=model_run.id,
                reason=REVIEW_REASON_PII_OUTPUT,
                summary="Seeded showcase review: output PII was detected and should be inspected before release.",
                priority=REVIEW_PRIORITY_HIGH,
            )
        created += 1

    db.commit()
    return created


def _seed_run_steps(db: Session, *, model_run: ModelRun, system: AISystem, input_pii_result: dict, output_pii_result: dict) -> None:
    create_run_step(
        db,
        model_run_id=model_run.id,
        step_type="approval_check",
        name="AI system approval check",
        status_="passed" if system.approval_status == "approved" else "blocked",
        input_summary=f"Approval status: {system.approval_status}; risk level: {system.risk_level}.",
        output_summary="Seeded showcase run uses the registered system approval state.",
        metadata={
            "ai_system_id": str(system.id),
            "approval_status": system.approval_status,
            "risk_level": system.risk_level,
        },
    )
    create_run_step(
        db,
        model_run_id=model_run.id,
        step_type="prompt_version_check",
        name="Prompt version check",
        status_="passed",
        input_summary="Seeded showcase run is linked to the active approved prompt version.",
        output_summary="Prompt matched the active prompt version.",
        metadata={"prompt_version_id": str(model_run.prompt_version_id) if model_run.prompt_version_id else None},
    )
    create_run_step(
        db,
        model_run_id=model_run.id,
        step_type="provider_call",
        name="LLM provider call",
        status_="completed",
        input_summary="Seeded showcase output represents a governed provider response.",
        output_summary=f"Provider returned output through model {model_run.model_name}.",
        metadata={
            "provider": model_run.model_provider,
            "model": model_run.model_name,
            "model_version": model_run.model_version,
            "estimated_cost_usd": model_run.cost_usd,
        },
        latency_ms=model_run.latency_ms,
    )
    create_run_step(
        db,
        model_run_id=model_run.id,
        step_type="pii_check",
        name="Input PII check",
        status_="requires_review" if input_pii_result.get("pii_detected") else "passed",
        input_summary="Seeded input text was scanned by the local PII detector.",
        output_summary=_seed_pii_summary("input", input_pii_result),
        metadata=input_pii_result,
    )
    create_run_step(
        db,
        model_run_id=model_run.id,
        step_type="pii_check",
        name="Output PII check",
        status_="requires_review" if output_pii_result.get("pii_detected") else "passed",
        input_summary="Seeded output text was scanned by the local PII detector.",
        output_summary=_seed_pii_summary("output", output_pii_result),
        metadata=output_pii_result,
    )


def _seed_pii_summary(source: str, result: dict) -> str:
    if not result.get("pii_detected"):
        return f"No PII detected in {source}."
    return f"PII detected in {source}: {', '.join(result.get('pii_types', []))}; confidence {result.get('confidence', 'low')}."


def seed_demo_evaluations(db: Session) -> int:
    settings = get_settings()
    evaluated_run_ids = set(db.scalars(select(Evaluation.model_run_id)).all())
    runs = db.scalars(select(ModelRun).where(ModelRun.output_text.is_not(None))).all()
    systems_by_id = {system.id: system for system in db.scalars(select(AISystem)).all()}
    created = 0
    for run in runs:
        if run.id in evaluated_run_ids:
            continue
        system = systems_by_id.get(run.ai_system_id)
        if system is None:
            continue
        evaluate_model_run(
            db,
            settings=settings,
            ai_system=system,
            model_run=run,
            retrieved_documents=[document.content for document in run.retrieved_documents],
            actor="seed:demo",
        )
        created += 1
    if created:
        db.commit()
    return created
