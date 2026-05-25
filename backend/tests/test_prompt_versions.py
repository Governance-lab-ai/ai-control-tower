import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient

from app.main import app
from tests.helpers.factories import make_ai_system_payload


def test_ai_system_gets_default_active_prompt_version() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/ai-systems",
            json=make_ai_system_payload(name=f"Prompt Version Default {uuid4()}"),
        )
        assert created.status_code == 201

        response = client.get(f"/ai-systems/{created.json()['id']}/prompt-versions")

    assert response.status_code == 200
    versions = response.json()
    assert len(versions) == 1
    assert versions[0]["status"] == "active"
    assert versions[0]["version"] == "v1"


def test_create_and_activate_prompt_version() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/ai-systems",
            json=make_ai_system_payload(name=f"Prompt Version Activation {uuid4()}"),
        )
        system_id = created.json()["id"]

        draft = client.post(
            f"/ai-systems/{system_id}/prompt-versions",
            json={
                "name": "Updated reviewer prompt",
                "prompt_text": "Use stricter reviewer language for synthetic test cases.",
            },
        )
        assert draft.status_code == 201

        approve = client.patch(f"/prompt-versions/{draft.json()['id']}/approve")
        activated = client.patch(f"/prompt-versions/{draft.json()['id']}/activate")
        versions = client.get(f"/ai-systems/{system_id}/prompt-versions").json()

    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"
    assert activated.status_code == 200
    assert activated.json()["status"] == "active"
    active_versions = [version for version in versions if version["status"] == "active"]
    retired_versions = [version for version in versions if version["status"] == "retired"]
    assert len(active_versions) == 1
    assert active_versions[0]["id"] == draft.json()["id"]
    assert retired_versions


def test_draft_prompt_version_cannot_be_activated_before_approval() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/ai-systems",
            json=make_ai_system_payload(name=f"Prompt Version Approval Required {uuid4()}"),
        )
        system_id = created.json()["id"]

        draft = client.post(
            f"/ai-systems/{system_id}/prompt-versions",
            json={
                "name": "Unapproved prompt",
                "prompt_text": "Draft prompt text should not activate yet.",
            },
        )
        activated = client.patch(f"/prompt-versions/{draft.json()['id']}/activate")

    assert activated.status_code == 409
    assert activated.json()["detail"]["code"] == "PROMPT_VERSION_NOT_APPROVED"


def test_retire_prompt_version() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/ai-systems",
            json=make_ai_system_payload(name=f"Prompt Version Retire {uuid4()}"),
        )
        system_id = created.json()["id"]
        versions = client.get(f"/ai-systems/{system_id}/prompt-versions").json()

        retired = client.patch(f"/prompt-versions/{versions[0]['id']}/retire")

    assert retired.status_code == 200
    assert retired.json()["status"] == "retired"
