import os
from uuid import UUID, uuid4

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models.audit_event import AuditEvent
from app.models.model_run import ModelRun, RetrievedDocument, RunStep
from app.services.prompt_versions import DEFAULT_PROMPT_TEXT
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
        "prompt": DEFAULT_PROMPT_TEXT,
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

    with SessionLocal() as db:
        model_run = db.get(ModelRun, UUID(body["run_id"]))
        retrieved_document_count = db.query(RetrievedDocument).filter(RetrievedDocument.model_run_id == UUID(body["run_id"])).count()
        run_steps = db.scalars(select(RunStep).where(RunStep.model_run_id == UUID(body["run_id"]))).all()

    assert model_run is not None
    assert model_run.status == "executed"
    assert model_run.prompt_version_id is not None
    assert model_run.latency_ms >= 1
    assert model_run.cost_usd > 0
    assert retrieved_document_count == 1
    assert {"approval_check", "policy_decision", "pii_check", "provider_call", "review_routing"}.issubset({step.step_type for step in run_steps})
    assert any(step.step_type == "prompt_version_check" and step.status == "passed" for step in run_steps)


def test_blocked_system_does_not_execute_and_records_audit_event() -> None:
    with TestClient(app) as client:
        system = _create_system(client, "blocked")
        response = client.post("/governance/run", json=_gateway_payload(system["id"]))

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "blocked"
    assert body["run_id"]
    assert body["output_text"] is None

    with SessionLocal() as db:
        actions = db.scalars(select(AuditEvent.action).where(AuditEvent.entity_id == UUID(system["id"]))).all()
        model_run = db.get(ModelRun, UUID(body["run_id"]))
        run_steps = db.scalars(select(RunStep).where(RunStep.model_run_id == UUID(body["run_id"]))).all()

    assert "governance.run.blocked" in actions
    assert model_run is not None
    assert model_run.status == "blocked"
    assert model_run.output_text is None
    assert any(step.step_type == "approval_check" and step.status == "blocked" for step in run_steps)


def test_pending_system_requires_review_without_execution_and_records_shell_run() -> None:
    with TestClient(app) as client:
        system = _create_system(client, "pending")
        response = client.post("/governance/run", json=_gateway_payload(system["id"]))

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "requires_review"
    assert body["run_id"]
    assert body["output_text"] is None
    assert "Review-required requests are not executed in the local MVP gateway." in body["governance_messages"]

    with SessionLocal() as db:
        model_run = db.get(ModelRun, UUID(body["run_id"]))
        run_steps = db.scalars(select(RunStep).where(RunStep.model_run_id == UUID(body["run_id"]))).all()

    assert model_run is not None
    assert model_run.status == "requires_review"
    assert model_run.output_text is None
    assert any(step.step_type == "approval_check" and step.status == "requires_review" for step in run_steps)
    assert any(step.step_type == "policy_decision" and step.status == "require_review" for step in run_steps)


def test_prompt_mismatch_requires_review_without_execution() -> None:
    with TestClient(app) as client:
        system = _create_system(client, "approved")
        payload = _gateway_payload(system["id"])
        payload["prompt"] = "Use an unapproved prompt for this request."
        response = client.post("/governance/run", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "requires_review"
    assert body["run_id"]
    assert body["output_text"] is None
    assert "Prompt text does not match active prompt version v1." in body["governance_messages"]

    with SessionLocal() as db:
        model_run = db.get(ModelRun, UUID(body["run_id"]))
        run_steps = db.scalars(select(RunStep).where(RunStep.model_run_id == UUID(body["run_id"]))).all()

    assert model_run is not None
    assert model_run.status == "requires_review"
    assert any(step.step_type == "prompt_version_check" and step.status == "requires_review" for step in run_steps)


def test_cross_system_prompt_version_is_blocked_without_execution() -> None:
    with TestClient(app) as client:
        first_system = _create_system(client, "approved")
        second_system = _create_system(client, "approved")
        first_prompt_version = client.get(f"/ai-systems/{first_system['id']}/prompt-versions").json()[0]
        payload = _gateway_payload(second_system["id"])
        payload["prompt_version_id"] = first_prompt_version["id"]
        response = client.post("/governance/run", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "blocked"
    assert "Requested prompt version does not belong to this AI system." in body["governance_messages"]

    with SessionLocal() as db:
        model_run = db.get(ModelRun, UUID(body["run_id"]))

    assert model_run is not None
    assert model_run.prompt_version_id is None
    assert model_run.output_text is None


def test_missing_system_returns_not_found() -> None:
    with TestClient(app) as client:
        response = client.post("/governance/run", json=_gateway_payload(str(uuid4())))

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "AI_SYSTEM_NOT_FOUND"
