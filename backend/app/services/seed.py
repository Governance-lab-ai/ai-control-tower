from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_system import AISystem
from app.models.model_run import ModelRun
from app.models.prompt_version import PromptVersion
from app.schemas.ai_system import AISystemCreate
from app.services.ai_systems import create_ai_system
from app.services.model_runs import create_model_run, estimate_local_cost_usd


DEMO_SYSTEMS: tuple[AISystemCreate, ...] = (
    AISystemCreate(
        name="Customer Support Summariser",
        description="Summarises synthetic customer support interactions for internal support managers.",
        department="Customer Operations",
        owner_name="Avery Stone",
        owner_email="avery.stone@example.test",
        model_provider="mock",
        model_name="mock-governance-summariser",
        data_sources=["support_tickets", "product_docs"],
        contains_personal_data=True,
        risk_level="medium",
        human_oversight_required=True,
        approval_status="pending",
    ),
    AISystemCreate(
        name="Sales Email Generator",
        description="Drafts synthetic outbound sales email variants from approved product messaging.",
        department="Revenue",
        owner_name="Morgan Vale",
        owner_email="morgan.vale@example.test",
        model_provider="mock",
        model_name="mock-email-drafter",
        data_sources=["product_messaging"],
        contains_personal_data=False,
        risk_level="low",
        human_oversight_required=False,
        approval_status="approved",
    ),
    AISystemCreate(
        name="HR CV Screening Assistant",
        description="Screens synthetic CV records for demonstration of high-risk governance controls.",
        department="People",
        owner_name="Jordan Reid",
        owner_email="jordan.reid@example.test",
        model_provider="mock",
        model_name="mock-cv-screening-assistant",
        data_sources=["candidate_profiles", "role_requirements"],
        contains_personal_data=True,
        risk_level="high",
        human_oversight_required=True,
        approval_status="blocked",
    ),
)


def seed_demo_systems(db: Session) -> int:
    existing_names = set(db.scalars(select(AISystem.name)).all())
    created = 0
    for payload in DEMO_SYSTEMS:
        if payload.name in existing_names:
            continue
        create_ai_system(db, payload)
        created += 1
    seed_demo_model_runs(db)
    return created


def seed_demo_model_runs(db: Session) -> int:
    existing_run_count = db.scalar(select(ModelRun).limit(1))
    if existing_run_count is not None:
        return 0

    systems_by_name = {system.name: system for system in db.scalars(select(AISystem)).all()}
    created = 0
    demo_runs = [
        {
            "system_name": "Sales Email Generator",
            "prompt": "Draft a short approved outreach email using product messaging only.",
            "input_text": "Synthetic prospect segment: operations leaders evaluating governance tooling.",
            "output_text": "Subject: Govern AI with confidence\n\nHi there, here is a concise approved outreach draft for governance-focused operations leaders.",
            "retrieved_documents": ["Approved product messaging brief for synthetic demo outreach."],
            "latency_ms": 84,
        },
        {
            "system_name": "Sales Email Generator",
            "prompt": "Create three subject line options using approved positioning.",
            "input_text": "Synthetic campaign for risk and compliance leaders.",
            "output_text": "1. Govern AI before risk scales\n2. Bring control to AI workflows\n3. Make AI use audit-ready",
            "retrieved_documents": ["Synthetic campaign positioning notes."],
            "latency_ms": 63,
        },
        {
            "system_name": "Customer Support Summariser",
            "prompt": "Summarise the support interaction for internal triage.",
            "input_text": "Synthetic support case describes a delayed shipment and refund request.",
            "output_text": "The customer is asking for shipment status and refund options. Escalate to a support reviewer before sending.",
            "retrieved_documents": ["Synthetic support policy: delayed shipment handling.", "Synthetic refund policy summary."],
            "latency_ms": 112,
        },
    ]

    for item in demo_runs:
        system = systems_by_name.get(item["system_name"])
        if system is None:
            continue
        prompt_version = PromptVersion(
            ai_system_id=system.id,
            version="v1",
            name=f"{system.name} demo prompt",
            prompt_text=item["prompt"],
            status="active",
        )
        db.add(prompt_version)
        db.flush()
        create_model_run(
            db,
            ai_system=system,
            prompt_version_id=prompt_version.id,
            prompt=item["prompt"],
            input_text=item["input_text"],
            output_text=item["output_text"],
            model_provider=system.model_provider,
            model_name=system.model_name,
            model_version="seed-demo-v1",
            latency_ms=item["latency_ms"],
            cost_usd=estimate_local_cost_usd(item["prompt"], item["input_text"], item["output_text"], item["retrieved_documents"]),
            status_="executed",
            retrieved_documents=item["retrieved_documents"],
        )
        created += 1

    db.commit()
    return created
