import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient

from app.main import app
from tests.helpers.factories import make_ai_system_payload


def _create_approved_system(client: TestClient) -> dict:
    response = client.post(
        "/ai-systems",
        json=make_ai_system_payload(
            name=f"Run API Test System {uuid4()}",
            approval_status="approved",
        ),
    )
    assert response.status_code == 201
    return response.json()


def _create_run(client: TestClient, system_id: str) -> dict:
    response = client.post(
        "/governance/run",
        json={
            "ai_system_id": system_id,
            "actor": "test:model-run-user",
            "prompt": "Summarise the synthetic case for a reviewer.",
            "input_text": "Synthetic customer asks whether a delayed order can be refunded.",
            "retrieved_documents": ["Synthetic refund policy.", "Synthetic shipping policy."],
            "metadata": {"source": "pytest"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "executed"
    return body


def test_model_run_detail_and_system_history_endpoints() -> None:
    with TestClient(app) as client:
        system = _create_approved_system(client)
        gateway_response = _create_run(client, system["id"])

        detail_response = client.get(f"/model-runs/{gateway_response['run_id']}")
        system_runs_response = client.get(f"/ai-systems/{system['id']}/runs")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == gateway_response["run_id"]
    assert detail["ai_system_id"] == system["id"]
    assert detail["prompt"] == "Summarise the synthetic case for a reviewer."
    assert detail["output_text"].startswith("[Local mock output]")
    assert detail["model_provider"] == "local_mock"
    assert detail["model_name"] == "mock-governance-gateway"
    assert detail["model_version"] == "local-mock-v1"
    assert detail["latency_ms"] >= 1
    assert detail["cost_usd"] > 0
    assert len(detail["retrieved_documents"]) == 2

    assert system_runs_response.status_code == 200
    system_runs = system_runs_response.json()
    assert any(run["id"] == gateway_response["run_id"] for run in system_runs)


def test_model_runs_list_includes_created_run() -> None:
    with TestClient(app) as client:
        system = _create_approved_system(client)
        gateway_response = _create_run(client, system["id"])
        list_response = client.get("/model-runs")

    assert list_response.status_code == 200
    runs = list_response.json()
    assert any(run["id"] == gateway_response["run_id"] for run in runs)
