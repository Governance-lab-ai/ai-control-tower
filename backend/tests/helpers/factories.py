from typing import Any


def make_ai_system_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": "Finance Policy Assistant",
        "description": "Answers synthetic internal finance policy questions for demo users.",
        "department": "Finance",
        "owner_name": "Taylor Quinn",
        "owner_email": "taylor.quinn@example.test",
        "model_provider": "mock",
        "model_name": "mock-policy-assistant",
        "data_sources": ["finance_policy_docs"],
        "contains_personal_data": False,
        "risk_level": "medium",
        "human_oversight_required": True,
        "approval_status": "pending",
    }
    payload.update(overrides)
    return payload
