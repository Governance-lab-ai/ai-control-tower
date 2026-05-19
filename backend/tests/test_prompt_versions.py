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

        activated = client.patch(f"/prompt-versions/{draft.json()['id']}/activate")
        versions = client.get(f"/ai-systems/{system_id}/prompt-versions").json()

    assert activated.status_code == 200
    assert activated.json()["status"] == "active"
    active_versions = [version for version in versions if version["status"] == "active"]
    retired_versions = [version for version in versions if version["status"] == "retired"]
    assert len(active_versions) == 1
    assert active_versions[0]["id"] == draft.json()["id"]
    assert retired_versions
