import os
from uuid import UUID, uuid4

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models.audit_event import AuditEvent
from app.models.incident import Incident
from app.models.model_run import ModelRun
from tests.helpers.factories import make_ai_system_payload


def _create_approved_system(client: TestClient) -> dict:
    response = client.post(
        "/ai-systems",
        json=make_ai_system_payload(
            name=f"PII Incident Test System {uuid4()}",
            approval_status="approved",
            contains_personal_data=True,
        ),
    )
    assert response.status_code == 201
    return response.json()


def test_gateway_creates_incident_for_synthetic_pii_input_and_output() -> None:
    with TestClient(app) as client:
        system = _create_approved_system(client)
        response = client.post(
            "/governance/run",
            json={
                "ai_system_id": system["id"],
                "actor": "test:pii-user",
                "prompt": "Summarise the case for review.",
                "input_text": "Customer name: Alex Morgan. Email alex.morgan@example.test. Account ID: ACCT-12345.",
                "retrieved_documents": [],
                "metadata": {"source": "pytest"},
            },
        )
        incidents_response = client.get("/incidents")
        run_incidents_response = client.get(f"/model-runs/{response.json()['run_id']}/incidents")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "requires_review"
    assert body["run_id"]

    with SessionLocal() as db:
        model_run = db.get(ModelRun, UUID(body["run_id"]))
        incidents = db.scalars(select(Incident).where(Incident.model_run_id == UUID(body["run_id"]))).all()

    assert model_run is not None
    assert model_run.status == "requires_review"
    assert model_run.input_pii_result["pii_detected"] is True
    assert model_run.output_pii_result["pii_detected"] is True
    assert {incident.incident_type for incident in incidents} == {"pii_detected_input", "pii_detected_output"}
    assert all("[REDACTED_" in incident.description for incident in incidents)

    assert incidents_response.status_code == 200
    assert any(incident["model_run_id"] == body["run_id"] for incident in incidents_response.json())
    assert run_incidents_response.status_code == 200
    assert {incident["incident_type"] for incident in run_incidents_response.json()} == {"pii_detected_input", "pii_detected_output"}


def test_gateway_does_not_create_incident_without_pii() -> None:
    with TestClient(app) as client:
        system = _create_approved_system(client)
        response = client.post(
            "/governance/run",
            json={
                "ai_system_id": system["id"],
                "actor": "test:pii-user",
                "prompt": "Summarise the case for review.",
                "input_text": "Synthetic support ticket asks for a delivery status update.",
                "retrieved_documents": [],
                "metadata": {"source": "pytest"},
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "executed"

    with SessionLocal() as db:
        model_run = db.get(ModelRun, UUID(body["run_id"]))
        incidents = db.scalars(select(Incident).where(Incident.model_run_id == UUID(body["run_id"]))).all()

    assert model_run is not None
    assert model_run.input_pii_result["pii_detected"] is False
    assert model_run.output_pii_result["pii_detected"] is False
    assert incidents == []


def test_incident_status_update_records_audit_event() -> None:
    with TestClient(app) as client:
        system = _create_approved_system(client)
        run_response = client.post(
            "/governance/run",
            json={
                "ai_system_id": system["id"],
                "actor": "test:pii-user",
                "prompt": "Summarise the case for review.",
                "input_text": "Customer name: Alex Morgan. Email alex.morgan@example.test.",
                "retrieved_documents": [],
                "metadata": {"source": "pytest"},
            },
        )
        incident = client.get(f"/model-runs/{run_response.json()['run_id']}/incidents").json()[0]
        update_response = client.patch(
            f"/incidents/{incident['id']}",
            json={"status": "under_review", "actor": "test:incident-reviewer", "notes": "Reviewer picked up the incident."},
        )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "under_review"

    with SessionLocal() as db:
        updated = db.get(Incident, UUID(incident["id"]))
        actions = db.scalars(select(AuditEvent.action).where(AuditEvent.entity_id == UUID(incident["id"]))).all()

    assert updated is not None
    assert updated.status == "under_review"
    assert "incident.status_changed" in actions
