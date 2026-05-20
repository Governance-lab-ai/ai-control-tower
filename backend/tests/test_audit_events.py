import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient

from app.main import app
from tests.helpers.factories import make_ai_system_payload


def test_audit_events_endpoint_returns_governance_events() -> None:
    with TestClient(app) as client:
        create_response = client.post(
            "/ai-systems",
            json=make_ai_system_payload(name=f"Audit API Test System {uuid4()}"),
        )
        assert create_response.status_code == 201

        response = client.get("/audit-events")
        entity_response = client.get(f"/audit-events?entity_id={create_response.json()['id']}")

    assert response.status_code == 200
    events = response.json()
    assert any(event["action"] == "ai_system.created" for event in events)
    assert all("metadata" in event for event in events)

    assert entity_response.status_code == 200
    assert any(event["entity_id"] == create_response.json()["id"] for event in entity_response.json())
