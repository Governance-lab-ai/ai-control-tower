import os

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient

from app.main import app


def test_policy_endpoint_denies_destructive_tool_action() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/policies/evaluate",
            json={
                "action_type": "tool_call",
                "actor": "test:agent",
                "context": {
                    "tool_name": "drop_table",
                    "action": "drop",
                    "allowed_tools": ["web_search", "database_read"],
                },
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["action"] == "deny"
    assert "deny-tool-not-granted" in body["matched_rules"]


def test_policy_endpoint_requires_review_for_high_impact_tool() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/policies/evaluate",
            json={
                "action_type": "tool_call",
                "actor": "test:agent",
                "context": {
                    "tool_name": "send_email",
                    "action": "send",
                    "allowed_tools": ["send_email"],
                },
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["action"] == "require_review"
    assert "review-high-impact-tool" in body["matched_rules"]


def test_policy_endpoint_requires_review_for_pending_model_execution() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/policies/evaluate",
            json={
                "action_type": "model_execution",
                "actor": "test:app",
                "context": {
                    "approval_status": "pending",
                    "risk_level": "medium",
                    "input_pii_detected": False,
                },
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["action"] == "require_review"
    assert "review-pending-system" in body["matched_rules"]
