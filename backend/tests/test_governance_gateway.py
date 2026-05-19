import os
from uuid import UUID, uuid4

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models.audit_event import AuditEvent
from tests.helpers.factories import make_ai_system_payload


def _create_system(client: TestClient, approval_status: str) -> dict:
    response = client.post(
        "/ai-systems",
        json=make_ai_system_payload(
            name=f"Gateway Test System {approval_status} {uuid4()}",
            approval_status=approval_status,
        ),
    )
    assert response.status_code == 201
    return response.json()


def _gateway_payload(system_id: str) -> dict:
    return {
        "ai_system_id": system_id,
        "actor": "test:gateway-user",
        "prompt": "Summarise the request using approved policy language.",
        "input_text": "Synthetic support ticket asks for a delivery status update.",
        "retrieved_documents": ["Synthetic delivery policy document."],
        "metadata": {"source": "pytest"},
    }


def test_approved_system_executes_through_gateway() -> None:
    with TestClient(app) as client:
        system = _create_system(client, "approved")
        response = client.post("/governance/run", json=_gateway_payload(system["id"]))

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "executed"
    assert body["run_id"]
    assert body["output_text"].startswith("[Local mock output]")
    assert "AI system is approved for gateway execution." in body["governance_messages"]


def test_blocked_system_does_not_execute_and_records_audit_event() -> None:
    with TestClient(app) as client:
        system = _create_system(client, "blocked")
        response = client.post("/governance/run", json=_gateway_payload(system["id"]))

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "blocked"
    assert body["run_id"] is None
    assert body["output_text"] is None

    with SessionLocal() as db:
        actions = db.scalars(select(AuditEvent.action).where(AuditEvent.entity_id == UUID(system["id"]))).all()

    assert "governance.run.blocked" in actions


def test_pending_system_requires_review_without_execution() -> None:
    with TestClient(app) as client:
        system = _create_system(client, "pending")
        response = client.post("/governance/run", json=_gateway_payload(system["id"]))

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "requires_review"
    assert body["run_id"] is None
    assert body["output_text"] is None
    assert "Pending systems are not executed in the local MVP gateway." in body["governance_messages"]


def test_missing_system_returns_not_found() -> None:
    with TestClient(app) as client:
        response = client.post("/governance/run", json=_gateway_payload(str(uuid4())))

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "AI_SYSTEM_NOT_FOUND"
