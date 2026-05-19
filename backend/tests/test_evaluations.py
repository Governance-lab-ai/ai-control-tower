import os
from uuid import UUID, uuid4

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.evaluation import Evaluation
from app.models.model_run import ModelRun
from app.providers.evaluation import EvaluationRequest, LocalEvaluationProvider
from tests.helpers.factories import make_ai_system_payload


def _create_system(client: TestClient, *, risk_level: str = "medium") -> dict:
    response = client.post(
        "/ai-systems",
        json=make_ai_system_payload(
            name=f"Evaluation Test System {risk_level} {uuid4()}",
            approval_status="approved",
            risk_level=risk_level,
        ),
    )
    assert response.status_code == 201
    return response.json()


def _gateway_payload(system_id: str) -> dict:
    return {
        "ai_system_id": system_id,
        "actor": "test:evaluation-user",
        "prompt": "Summarise the request using approved policy language.",
        "input_text": "Synthetic support ticket asks for a delivery status update.",
        "retrieved_documents": ["Synthetic delivery policy document."],
        "metadata": {"source": "pytest"},
    }


def test_gateway_creates_evaluation_for_executed_run() -> None:
    with TestClient(app) as client:
        system = _create_system(client, risk_level="medium")
        response = client.post("/governance/run", json=_gateway_payload(system["id"]))
        evaluations_response = client.get("/evaluations")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "executed"
    assert "Evaluation queued for asynchronous local processing." in body["governance_messages"]

    with SessionLocal() as db:
        model_run = db.get(ModelRun, UUID(body["run_id"]))
        evaluation = db.query(Evaluation).filter(Evaluation.model_run_id == UUID(body["run_id"])).one_or_none()

    assert model_run is not None
    assert evaluation is not None
    assert evaluation.evaluation_score >= evaluation.threshold
    assert evaluation.requires_human_review is False

    assert evaluations_response.status_code == 200
    assert any(item["model_run_id"] == body["run_id"] for item in evaluations_response.json())


def test_high_risk_low_score_evaluation_routes_run_to_review() -> None:
    with TestClient(app) as client:
        system = _create_system(client, risk_level="high")
        payload = _gateway_payload(system["id"])
        payload["retrieved_documents"] = []
        response = client.post("/governance/run", json=payload)
        failed_response = client.get("/evaluations?failed_only=true")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "executed"

    with SessionLocal() as db:
        model_run = db.get(ModelRun, UUID(body["run_id"]))
        evaluation = db.query(Evaluation).filter(Evaluation.model_run_id == UUID(body["run_id"])).one_or_none()

    assert model_run is not None
    assert model_run.status == "requires_review"
    assert evaluation is not None
    assert evaluation.requires_human_review is True
    assert evaluation.evaluation_score < evaluation.threshold

    assert failed_response.status_code == 200
    assert any(item["model_run_id"] == body["run_id"] for item in failed_response.json())


def test_local_evaluation_provider_flags_hallucination_signal() -> None:
    system = type("SyntheticSystem", (), {"risk_level": "medium"})()
    result = LocalEvaluationProvider().evaluate(
        EvaluationRequest(
            ai_system=system,
            prompt="Answer from approved retrieved context only.",
            input_text="Synthetic support case.",
            output_text="This contains an unsupported claim not in the retrieved context.",
            retrieved_documents=["Approved context says only to escalate the synthetic case."],
            threshold=70,
        )
    )

    assert result.hallucination_flag is True
    assert result.requires_human_review is True
