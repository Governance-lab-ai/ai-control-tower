from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_system import AISystem
from app.schemas.ai_system import AISystemCreate
from app.services.ai_systems import create_ai_system


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
    return created
