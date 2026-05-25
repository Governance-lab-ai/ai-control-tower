import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient

from app.main import app
from app.services.prompt_versions import DEFAULT_PROMPT_TEXT
from tests.helpers.factories import make_ai_system_payload


def _create_system(client: TestClient, *, department: str, risk_level: str = "medium") -> dict:
    response = client.post(
        "/ai-systems",
        json=make_ai_system_payload(
            name=f"Dashboard Test System {department} {risk_level} {uuid4()}",
            department=department,
            approval_status="approved",
            risk_level=risk_level,
            contains_personal_data=True,
        ),
    )
    assert response.status_code == 201
    return response.json()


def _run_gateway(client: TestClient, system_id: str, *, input_text: str, retrieved_documents: list[str]) -> dict:
    response = client.post(
        "/governance/run",
        json={
            "ai_system_id": system_id,
            "actor": "test:dashboard-user",
            "prompt": DEFAULT_PROMPT_TEXT,
            "input_text": input_text,
            "retrieved_documents": retrieved_documents,
            "metadata": {"source": "pytest-dashboard"},
        },
    )
    assert response.status_code == 200
    return response.json()


def test_dashboard_summary_returns_governance_metrics() -> None:
    with TestClient(app) as client:
        support_system = _create_system(client, department="Customer Operations", risk_level="medium")
        risk_system = _create_system(client, department="People", risk_level="high")
        _run_gateway(
            client,
            support_system["id"],
            input_text="Customer name: Alex Morgan. Email: alex.morgan@example.test. Please summarise this support ticket.",
            retrieved_documents=["Synthetic support policy."],
        )
        _run_gateway(
            client,
            risk_system["id"],
            input_text="Synthetic high-risk request with no grounding context.",
            retrieved_documents=[],
        )

        response = client.get("/dashboard/summary")

    assert response.status_code == 200
    summary = response.json()
    assert summary["total_ai_systems"] >= 2
    assert summary["systems_by_risk"]["medium"] >= 1
    assert summary["systems_by_risk"]["high"] >= 1
    assert summary["systems_by_department"]["Customer Operations"] >= 1
    assert summary["pending_reviews"] >= 1
    assert summary["open_incidents"] >= 1
    assert summary["failed_evaluations"] >= 1
    assert summary["total_runs"] >= 2
    assert summary["total_cost_usd"] > 0
    assert summary["average_latency_ms"] >= 0
    assert any(cell["department"] == "People" and cell["risk_level"] == "high" for cell in summary["risk_heatmap"])
    assert summary["usage_by_model"]


def test_audit_export_returns_filtered_json_and_csv() -> None:
    with TestClient(app) as client:
        system = _create_system(client, department="Audit Export", risk_level="critical")
        _run_gateway(
            client,
            system["id"],
            input_text="Customer name: Taylor Quinn. Email: taylor.quinn@example.test.",
            retrieved_documents=["Synthetic audit export policy."],
        )

        json_response = client.get("/audit/export?format=json&department=Audit%20Export")
        csv_response = client.get("/audit/export?format=csv&department=Audit%20Export")
        incident_response = client.get("/audit/export?format=json&incident_type=pii_detected_input")

    assert json_response.status_code == 200
    events = json_response.json()
    assert any(event["action"] == "ai_system.created" for event in events)
    assert any(event["action"].startswith("governance.run.") for event in events)

    assert csv_response.status_code == 200
    assert csv_response.headers["content-type"].startswith("text/csv")
    assert "id,created_at,actor,action,entity_type,entity_id,summary,metadata" in csv_response.text.splitlines()[0]

    assert incident_response.status_code == 200
    assert any(event["action"] == "incident.created" for event in incident_response.json())
