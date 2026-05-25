import os

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models.ai_system import AISystem
from app.models.audit_event import AuditEvent
from app.models.human_review import HumanReview
from app.models.model_run import ModelRun
from app.models.prompt_version import PromptVersion
from app.services.seed import clear_all_application_data


def test_clear_all_application_data_removes_local_records() -> None:
    with TestClient(app) as client:
        response = client.get("/ai-systems")

    assert response.status_code == 200
    assert response.json()

    with SessionLocal() as db:
        counts = clear_all_application_data(db)
        remaining_systems = db.scalars(select(AISystem)).all()
        remaining_audit_events = db.scalars(select(AuditEvent)).all()

    assert counts["ai_systems"] >= 1
    assert remaining_systems == []
    assert remaining_audit_events == []


def test_showcase_seed_contains_prompt_versions_runs_and_reviews() -> None:
    with TestClient(app) as client:
        systems_response = client.get("/ai-systems")
        reviews_response = client.get("/reviews")

    assert systems_response.status_code == 200
    names = {system["name"] for system in systems_response.json()}
    assert {
        "Customer Support Summariser",
        "Sales Email Generator",
        "HR CV Screening Assistant",
        "Procurement Policy Assistant",
    }.issubset(names)

    with SessionLocal() as db:
        active_showcase_prompts = db.scalars(
            select(PromptVersion).where(
                PromptVersion.name == "Approved showcase prompt",
                PromptVersion.status == "active",
            )
        ).all()
        runs = db.scalars(select(ModelRun)).all()
        reviews = db.scalars(select(HumanReview)).all()

    assert len(active_showcase_prompts) >= 4
    assert len(runs) >= 4
    assert any(review.reason == "pii_detected_input" for review in reviews)
    assert any(item["reason"] == "pii_detected_input" for item in reviews_response.json())
