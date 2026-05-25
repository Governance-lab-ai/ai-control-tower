import os
from uuid import UUID, uuid4

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models.audit_event import AuditEvent
from app.models.human_review import HumanReview
from app.services.prompt_versions import DEFAULT_PROMPT_TEXT
from tests.helpers.factories import make_ai_system_payload


def _create_system(client: TestClient, *, risk_level: str = "medium", human_oversight_required: bool = True) -> dict:
    response = client.post(
        "/ai-systems",
        json=make_ai_system_payload(
            name=f"Review Test System {risk_level} {uuid4()}",
            approval_status="approved",
            risk_level=risk_level,
            human_oversight_required=human_oversight_required,
        ),
    )
    assert response.status_code == 201
    return response.json()


def _create_pending_system(client: TestClient) -> dict:
    response = client.post(
        "/ai-systems",
        json=make_ai_system_payload(
            name=f"Pending Review Test System {uuid4()}",
            approval_status="pending",
            risk_level="medium",
            human_oversight_required=True,
        ),
    )
    assert response.status_code == 201
    return response.json()


def _run_payload(system_id: str, *, input_text: str, retrieved_documents: list[str] | None = None) -> dict:
    return {
        "ai_system_id": system_id,
        "actor": "test:review-user",
        "prompt": DEFAULT_PROMPT_TEXT,
        "input_text": input_text,
        "retrieved_documents": retrieved_documents or ["Synthetic delivery policy document."],
        "metadata": {"source": "pytest"},
    }


def test_pii_run_creates_pending_human_review() -> None:
    with TestClient(app) as client:
        system = _create_system(client)
        run_response = client.post(
            "/governance/run",
            json=_run_payload(system["id"], input_text="Customer name: Alex Morgan. Email alex.morgan@example.test."),
        )
        reviews_response = client.get("/reviews")

    assert run_response.status_code == 200
    body = run_response.json()
    assert body["status"] == "requires_review"

    assert reviews_response.status_code == 200
    reviews = reviews_response.json()
    matching_reviews = [item for item in reviews if item["model_run_id"] == body["run_id"]]
    assert any(item["status"] == "pending" for item in matching_reviews)
    assert any(item["reason"] == "pii_detected_input" for item in matching_reviews)


def test_pii_pending_shell_creates_human_review() -> None:
    with TestClient(app) as client:
        system = _create_pending_system(client)
        run_response = client.post(
            "/governance/run",
            json=_run_payload(system["id"], input_text="Customer name: Alex Morgan. Email alex.morgan@example.test."),
        )
        reviews_response = client.get("/reviews")

    assert run_response.status_code == 200
    body = run_response.json()
    assert body["status"] == "requires_review"

    reviews = reviews_response.json()
    assert any(item["model_run_id"] == body["run_id"] and item["reason"] == "pii_detected_input" for item in reviews)


def test_failed_evaluation_creates_review_and_decision_audit_event() -> None:
    with TestClient(app) as client:
        system = _create_system(client, risk_level="critical", human_oversight_required=False)
        run_response = client.post(
            "/governance/run",
            json=_run_payload(
                system["id"],
                input_text="Synthetic support ticket asks for a delivery status update.",
                retrieved_documents=[],
            ),
        )
        reviews_response = client.get("/reviews")

    assert run_response.status_code == 200
    run_id = run_response.json()["run_id"]
    reviews = reviews_response.json()
    review = next(item for item in reviews if item["model_run_id"] == run_id and item["reason"] == "evaluation_below_threshold")

    with TestClient(app) as client:
        decision_response = client.post(
            f"/reviews/{review['id']}/decision",
            json={
                "decision": "rejected",
                "reviewer_id": "reviewer-1",
                "reviewer_name": "Riley Reviewer",
                "notes": "Rejected because the local evaluation score is below the high-risk threshold.",
            },
        )

    assert decision_response.status_code == 200
    decided = decision_response.json()
    assert decided["status"] == "rejected"
    assert decided["reviewer_name"] == "Riley Reviewer"
    assert decided["decision_notes"].startswith("Rejected because")

    with SessionLocal() as db:
        audit_actions = db.scalars(select(AuditEvent.action).where(AuditEvent.entity_id == UUID(review["id"]))).all()
        stored_review = db.get(HumanReview, UUID(review["id"]))

    assert "human_review.rejected" in audit_actions
    assert stored_review is not None
    assert stored_review.decided_at is not None


def test_high_risk_human_oversight_creates_review() -> None:
    with TestClient(app) as client:
        system = _create_system(client, risk_level="high", human_oversight_required=True)
        run_response = client.post(
            "/governance/run",
            json=_run_payload(system["id"], input_text="Synthetic support ticket asks for a delivery status update."),
        )
        reviews_response = client.get("/reviews")

    run_id = run_response.json()["run_id"]
    reviews = reviews_response.json()
    assert any(item["model_run_id"] == run_id and item["reason"] == "high_risk_human_oversight" for item in reviews)


def test_decided_review_cannot_be_decided_twice() -> None:
    with TestClient(app) as client:
        system = _create_system(client)
        run_response = client.post(
            "/governance/run",
            json=_run_payload(system["id"], input_text="Customer name: Alex Morgan. Email alex.morgan@example.test."),
        )
        review = next(item for item in client.get("/reviews").json() if item["model_run_id"] == run_response.json()["run_id"])
        first = client.post(
            f"/reviews/{review['id']}/decision",
            json={
                "decision": "approved",
                "reviewer_id": "reviewer-2",
                "reviewer_name": "Avery Approver",
                "notes": "Approved for synthetic test use.",
            },
        )
        second = client.post(
            f"/reviews/{review['id']}/decision",
            json={
                "decision": "escalated",
                "reviewer_id": "reviewer-3",
                "reviewer_name": "Case Escalator",
                "notes": "Trying to decide twice.",
            },
        )

    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "HUMAN_REVIEW_ALREADY_DECIDED"
