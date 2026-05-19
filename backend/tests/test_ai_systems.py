import os
from uuid import UUID

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.db.session import SessionLocal
from app.models.audit_event import AuditEvent
from tests.helpers.factories import make_ai_system_payload


def test_seeded_systems_are_available() -> None:
    with TestClient(app) as client:
        response = client.get("/ai-systems")

    assert response.status_code == 200
    names = {system["name"] for system in response.json()}
    assert "Customer Support Summariser" in names
    assert "Sales Email Generator" in names
    assert "HR CV Screening Assistant" in names


def test_create_ai_system_records_audit_event() -> None:
    with TestClient(app) as client:
        response = client.post("/ai-systems", json=make_ai_system_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["name"] == "Finance Policy Assistant"

    with SessionLocal() as db:
        audit_actions = db.scalars(select(AuditEvent.action).where(AuditEvent.entity_id == UUID(body["id"]))).all()

    assert "ai_system.created" in audit_actions


def test_get_ai_system_and_update_approval_status() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/ai-systems",
            json=make_ai_system_payload(
                name="Legal Clause Checker",
                description="Checks synthetic contract clauses against internal policy examples.",
                department="Legal",
                owner_name="Riley Chen",
                owner_email="riley.chen@example.test",
                model_provider="mock",
                model_name="mock-clause-checker",
                data_sources=["contract_playbook"],
                risk_level="low",
            ),
        ).json()

        detail_response = client.get(f"/ai-systems/{created['id']}")
        assert detail_response.status_code == 200
        assert detail_response.json()["name"] == "Legal Clause Checker"

        patch_response = client.patch(f"/ai-systems/{created['id']}/approval-status", json={"approval_status": "approved"})
        assert patch_response.status_code == 200
        assert patch_response.json()["approval_status"] == "approved"

    with SessionLocal() as db:
        audit_actions = db.scalars(select(AuditEvent.action).where(AuditEvent.entity_id == UUID(created["id"]))).all()

    assert "ai_system.approval_status_changed" in audit_actions


def test_invalid_risk_level_is_rejected() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/ai-systems",
            json=make_ai_system_payload(
                name="Invalid Risk System",
                description="Attempts to use a risk level outside the supported governance taxonomy.",
                department="Risk",
                owner_name="Casey Lee",
                owner_email="casey.lee@example.test",
                model_provider="mock",
                model_name="mock-invalid",
                data_sources=[],
                risk_level="severe",
            ),
        )

    assert response.status_code == 422
