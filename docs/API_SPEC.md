# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-12  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


## API design principles

- Prefix stable production API routes with `/api/v1`; Episode 1 and 2 local MVP routes currently expose root paths such as `/health` and `/ai-systems` to match the runnable scaffold.
- Use JSON request/response bodies.
- Use stable error codes.
- Enforce permissions in backend.
- Use pagination for list endpoints.
- Never expose secrets.
- Return governance metadata for model runs.
- Keep response shapes typed and documented.

## Common response conventions

### Pagination

```json
{
  "items": [],
  "page": 1,
  "page_size": 25,
  "total": 128
}
```

### Error

```json
{
  "error": {
    "code": "AI_SYSTEM_NOT_APPROVED",
    "message": "This AI system is not approved for model execution.",
    "details": {
      "system_id": "sys_123",
      "approval_status": "pending"
    }
  }
}
```

### Governance metadata

```json
{
  "route_decision": "hold_for_review",
  "route_reasons": [
    "PII detected in output",
    "System risk level is medium",
    "Human oversight required"
  ],
  "review_required": true,
  "incident_created": false
}
```

## Health

### `GET /api/v1/health`

Returns app status.

Response:

```json
{
  "status": "ok",
  "database": "ok",
  "version": "0.1.0",
  "environment": "local"
}
```

## AI systems

### `POST /ai-systems`

Create an AI system.

Request:

```json
{
  "name": "Customer Support Summariser",
  "description": "Summarises customer support tickets and suggests response drafts.",
  "department": "Customer Success",
  "owner_name": "Head of Support",
  "owner_email": "support-lead@example.test",
  "model_provider": "azure_openai",
  "model_name": "gpt-4.1",
  "data_sources": ["Zendesk", "CRM", "Product Docs"],
  "contains_personal_data": true,
  "human_oversight_required": true,
  "risk_level": "medium",
  "approval_status": "pending"
}
```

Response:

```json
{
  "id": "sys_001",
  "name": "Customer Support Summariser",
  "description": "Summarises customer support tickets and suggests response drafts.",
  "department": "Customer Success",
  "owner_name": "Head of Support",
  "owner_email": "support-lead@example.test",
  "model_provider": "azure_openai",
  "model_name": "gpt-4.1",
  "data_sources": ["Zendesk", "CRM", "Product Docs"],
  "contains_personal_data": true,
  "human_oversight_required": true,
  "risk_level": "medium",
  "approval_status": "pending",
  "created_at": "2026-05-12T09:00:00Z",
  "updated_at": "2026-05-12T09:00:00Z"
}
```

### `GET /ai-systems`

Response:

```json
[
  {
    "id": "sys_001",
    "name": "Customer Support Summariser",
    "department": "Customer Success",
    "owner_name": "Head of Support",
    "model_provider": "azure_openai",
    "model_name": "gpt-4.1",
    "risk_level": "medium",
    "approval_status": "approved",
    "contains_personal_data": true,
    "human_oversight_required": true,
    "created_at": "2026-05-12T09:00:00Z",
    "updated_at": "2026-05-12T09:00:00Z"
  }
]
```

### `GET /ai-systems/{system_id}`

Returns detail view data.

Includes:

- System metadata.
- Data sources.
- Active prompt version.
- Recent runs.
- Recent incidents.
- Approval history.
- Summary stats.

### `PATCH /ai-systems/{system_id}`

Update metadata. Approval status should use separate endpoint.

### `PATCH /ai-systems/{system_id}/approval-status`

Request:

```json
{
  "approval_status": "approved"
}
```

Response:

```json
{
  "id": "sys_001",
  "approval_status": "approved",
  "updated_at": "2026-05-12T09:10:00Z"
}
```

Creating a system records an `ai_system.created` audit event. Changing approval status records an `ai_system.approval_status_changed` audit event.

## Governance gateway

### `POST /governance/run`

Runs a request through the governance gateway instead of calling a model provider directly.

Request:

```json
{
  "ai_system_id": "11111111-1111-1111-1111-111111111111",
  "actor": "local_mock:governance_admin",
  "prompt": "Summarise the request using approved policy language.",
  "input_text": "Synthetic support ticket asks for a delivery status update.",
  "retrieved_documents": [
    "Synthetic delivery policy document."
  ],
  "metadata": {
    "source": "system_detail_test_run"
  }
}
```

Executed response:

```json
{
  "run_id": "22222222-2222-2222-2222-222222222222",
  "status": "executed",
  "output_text": "[Local mock output] Customer Support Summariser processed the request.",
  "governance_messages": [
    "AI system is approved for gateway execution.",
    "Executed through provider local_mock using model mock-governance-gateway.",
    "Model run logged with latency 84ms and estimated cost $0.000065."
  ]
}
```

Blocked response:

```json
{
  "run_id": "44444444-4444-4444-4444-444444444444",
  "status": "blocked",
  "output_text": null,
  "governance_messages": [
    "Execution blocked because approval status is blocked.",
    "No model provider call was made.",
    "Blocked attempt was logged as a model run shell for audit review."
  ]
}
```

Episode 3 gateway rules:

- Missing AI system returns `404` with `AI_SYSTEM_NOT_FOUND`.
- `approved` systems execute through the configured backend `LLMProvider`.
- `pending` systems return `requires_review`, do not execute, and create a model-run shell.
- `blocked` and `retired` systems return `blocked`, do not execute, and create a model-run shell.
- Gateway attempts create audit events with actions such as `governance.run.executed`, `governance.run.blocked`, and `governance.run.requires_review`.
- Gateway attempts create persistent `model_runs` records and one `retrieved_documents` row for each supplied retrieved document. Non-executed shells have `output_text: null`, `latency_ms: 0`, `cost_usd: 0`, and `model_version: "not_executed"`.
- Failed provider calls create `failed` model-run shell records and run-step evidence so the attempted provider, latency, and error are inspectable.
- `run_steps` records approval, PII, provider call, evaluation, and review-routing evidence for each run. It logs structured decisions and metadata, not private model chain-of-thought.

## Model runs

### `GET /model-runs`

Returns all persisted model runs, newest first.

### `GET /model-runs/{run_id}`

Returns one model run with retrieved documents.

### `GET /model-runs/{run_id}/incidents`

Returns incidents linked to one model run, newest first. Review detail pages use this targeted endpoint instead of fetching all incidents and filtering in the frontend.

Response:

```json
{
  "id": "22222222-2222-2222-2222-222222222222",
  "ai_system_id": "11111111-1111-1111-1111-111111111111",
  "prompt_version_id": "55555555-5555-5555-5555-555555555555",
  "prompt": "Summarise the request using approved policy language.",
  "input_text": "Synthetic support ticket asks for a delivery status update.",
  "output_text": "[Local mock output] Customer Support Summariser processed the request.",
  "model_provider": "local_mock",
  "model_name": "mock-governance-gateway",
  "model_version": "local-mock-v1",
  "latency_ms": 84,
  "cost_usd": 0.000065,
  "status": "executed",
  "input_pii_result": {
    "pii_detected": false,
    "pii_types": [],
    "locations": [],
    "confidence": "low"
  },
  "output_pii_result": {
    "pii_detected": false,
    "pii_types": [],
    "locations": [],
    "confidence": "low"
  },
  "evaluation": {
    "id": "44444444-4444-4444-4444-444444444444",
    "model_run_id": "22222222-2222-2222-2222-222222222222",
    "ai_system_id": "11111111-1111-1111-1111-111111111111",
    "provider": "local_heuristic",
    "evaluation_score": 82,
    "relevance_score": 88,
    "groundedness_score": 74,
    "hallucination_flag": false,
    "evaluation_summary": "Local heuristic evaluation signal.",
    "requires_human_review": false,
    "threshold": 70,
    "created_at": "2026-05-19T10:00:00Z"
  },
  "created_at": "2026-05-19T10:00:00Z",
  "retrieved_documents": [
    {
      "id": "33333333-3333-3333-3333-333333333333",
      "model_run_id": "22222222-2222-2222-2222-222222222222",
      "source_label": "retrieved_document_1",
      "content": "Synthetic delivery policy document.",
      "ordinal": 1,
      "created_at": "2026-05-19T10:00:00Z"
    }
  ],
  "run_steps": [
    {
      "id": "66666666-6666-6666-6666-666666666666",
      "model_run_id": "22222222-2222-2222-2222-222222222222",
      "step_type": "provider_call",
      "name": "LLM provider call",
      "status": "completed",
      "input_summary": "Provider local_mock received the governed prompt and input.",
      "output_summary": "Provider returned output through model mock-governance-gateway.",
      "metadata": {
        "provider": "local_mock",
        "model": "mock-governance-gateway",
        "model_version": "local-mock-v1"
      },
      "latency_ms": 84,
      "created_at": "2026-05-19T10:00:00Z"
    }
  ]
}
```

### `GET /ai-systems/{system_id}/runs`

Returns model runs for a selected AI system, newest first.

## PII detection and incidents

Episode 5 adds hybrid local PII checks before and after model execution. This is a prototype detector for synthetic demos and obvious structured values, not comprehensive PII discovery.

Detected patterns:

- Email addresses.
- Phone numbers.
- Names with labels such as `Customer name:`.
- Account IDs with labels such as `Account ID:`.
- Addresses with labels such as `Address:`.
- Dates of birth, national IDs, and postal codes with labels.
- Spaced IBAN-like values.
- Payment-card-like values that pass a Luhn checksum.

If PII is detected in input or output:

- The model run stores `input_pii_result` and/or `output_pii_result`.
- The run status is set to `requires_review` for executed runs.
- A PII incident is created with redacted snippets only.

Synthetic demo input:

```text
Customer name: Alex Morgan. Email alex.morgan@example.test. Account ID: ACCT-12345.
```

### `GET /incidents`

Returns all incidents, newest first.

### `GET /incidents/{incident_id}`

Returns one incident.

### `PATCH /incidents/{incident_id}`

Updates incident status and records an audit event.

Request:

```json
{
  "status": "under_review",
  "actor": "local-reviewer",
  "notes": "Reviewer has started investigation."
}
```

### `GET /ai-systems/{system_id}/incidents`

Returns incidents for a selected AI system.

## Prompt versions

### `GET /ai-systems/{system_id}/prompt-versions`

List prompt versions for a system.

### `POST /ai-systems/{system_id}/prompt-versions`

Create draft prompt version.

Request:

```json
{
  "name": "Support summariser v2",
  "prompt_text": "Summarise the support ticket. Do not include payment data. If personal data is present, minimise it."
}
```

### `PATCH /prompt-versions/{prompt_version_id}/activate`

Activate prompt version. Activating one version retires the previous active version for that system. Newly registered systems receive a default active `v1` prompt version.

## Model runs

### `GET /model-runs`

Query params:

```text
ai_system_id
department
route_decision
risk_level
evaluation_passed
pii_detected
start_date
end_date
page
page_size
```

### `GET /model-runs/{run_id}`

Returns full detail for authorised users:

- Prompt.
- Input.
- Output.
- Retrieved documents.
- Model metadata.
- Cost/latency.
- Evaluation result.
- Review status.
- Incident links.
- Audit event links.
- Gateway step timeline.

### `GET /model-runs/{run_id}/incidents`

Returns incidents linked to the selected model run, newest first.

## Evaluations

Episode 6 adds local prototype evaluations for executed model runs. Executed gateway calls queue asynchronous local evaluation after the run is logged. The evaluation record is usually available immediately in local development, but clients should treat it as eventually available.

### `GET /evaluations`

Returns evaluations, newest first. Use `?failed_only=true` to return only evaluations that require human review.

### `GET /evaluations/{evaluation_id}`

Returns one evaluation.

Evaluation fields:

- `provider`: evaluation provider, for example `local_heuristic`, `semantic_local_heuristic`, or `ollama_local_judge`.
- `evaluation_score`: weighted local/provider score from 0 to 100.
- `relevance_score`: relevance signal from 0 to 100.
- `groundedness_score`: retrieved-context support signal from 0 to 100.
- `hallucination_flag`: heuristic or provider flag for explicit unsupported-claim signals or very weak grounding.
- `requires_human_review`: true when the score is below the configured risk threshold or hallucination is flagged.

These are prototype governance signals, not proof that an answer is correct.

## Human reviews

Episode 7 adds the local human review queue. Review items are created automatically from risky gateway/evaluation outcomes and can be decided by a reviewer.

### `GET /reviews`

Query params:

```text
status
```

Returns review rows, newest first. The MVP defaults to `status=pending`; pass another status to inspect decided reviews.

Response item:

```json
{
  "id": "55555555-5555-5555-5555-555555555555",
  "ai_system_id": "11111111-1111-1111-1111-111111111111",
  "model_run_id": "22222222-2222-2222-2222-222222222222",
  "status": "pending",
  "reason": "pii_detected_output",
  "priority": "high",
  "summary": "Output PII was detected and requires reviewer confirmation.",
  "reviewer_id": null,
  "reviewer_name": null,
  "decision_notes": null,
  "decided_at": null,
  "created_at": "2026-05-19T12:00:00Z",
  "updated_at": "2026-05-19T12:00:00Z"
}
```

### `GET /reviews/{review_id}`

Returns review detail including linked model run evidence, retrieved documents, PII flags, and evaluation result.

### `POST /reviews/{review_id}/decision`

Request:

```json
{
  "decision": "approved",
  "reviewer_id": "local-reviewer",
  "reviewer_name": "Local Reviewer",
  "notes": "Output is acceptable after confirming the email address is not included in the response."
}
```

Response:

```json
{
  "id": "55555555-5555-5555-5555-555555555555",
  "status": "approved",
  "reviewer_id": "local-reviewer",
  "reviewer_name": "Local Reviewer",
  "decision_notes": "Output is acceptable after confirming the email address is not included in the response.",
  "decided_at": "2026-05-19T12:10:00Z"
}
```

Decision values are `approved`, `rejected`, and `escalated`. Decisions are allowed only while the review is `pending`. The backend records `human_review.created` when a review is queued and `human_review.approved`, `human_review.rejected`, or `human_review.escalated` when a reviewer decides it.

Automatic review creation rules:

- PII detected in input.
- PII detected in output.
- Evaluation requires review because the score is below threshold.
- Evaluation raises a hallucination flag.
- High-risk systems with human oversight required generate output.

## Audit events

### `GET /audit-events`

Returns append-only audit events, newest first. Optional filters are `actor`, `action`, `entity_type`, `entity_id`, and `limit`.

### `GET /audit-events/{event_id}`

Returns one audit event.

## Future filtered incident APIs

The local MVP currently exposes root incident endpoints documented above. Stable `/api/v1` filtered routes remain planned.

### `GET /api/v1/incidents`

Query params:

```text
status
severity
type
system_id
start_date
end_date
page
page_size
```

### `GET /api/v1/incidents/{incident_id}`

Returns incident detail.

### `PATCH /api/v1/incidents/{incident_id}`

Request:

```json
{
  "status": "resolved",
  "actor": "local-reviewer",
  "notes": "Prompt updated to redact email addresses. Reviewer training note added."
}
```

## Future audit export APIs

The local MVP currently exposes `GET /audit-events` and `GET /audit-events/{event_id}`. Filtered export remains planned.

### `GET /api/v1/audit-events`

Query params:

```text
action
entity_type
entity_id
actor_user_id
start_date
end_date
page
page_size
```

### `GET /api/v1/audit-events/export`

Exports CSV or JSON.

Query params:

```text
format=csv|json
start_date
end_date
entity_type
system_id
```

Requires elevated permission.

## Dashboard

### `GET /api/v1/dashboard/overview`

Response:

```json
{
  "summary": {
    "ai_systems_total": 24,
    "model_runs_30d": 128621,
    "failed_evaluations_30d": 312,
    "pii_incidents_30d": 27,
    "total_cost_30d": 12430.0,
    "human_reviews_pending": 7
  },
  "risk_posture": {
    "score": 72,
    "low": 8,
    "medium": 11,
    "high": 3,
    "critical": 0,
    "unknown": 2
  },
  "recent_incidents": []
}
```

### `GET /api/v1/dashboard/risk-heatmap`

Response:

```json
{
  "departments": ["Customer Success", "Sales", "Marketing", "Finance", "HR"],
  "columns": ["low", "medium", "high", "critical"],
  "cells": [
    {"department": "Customer Success", "risk_level": "low", "count": 3},
    {"department": "Customer Success", "risk_level": "medium", "count": 4},
    {"department": "Customer Success", "risk_level": "high", "count": 1},
    {"department": "Customer Success", "risk_level": "critical", "count": 0}
  ]
}
```

### `GET /api/v1/dashboard/cost-summary`

Returns cost by model, department, system, and day.

## Settings and integrations

### `GET /api/v1/integrations`

Returns integration card state.

### `PATCH /api/v1/integrations/{integration_id}`

Updates non-secret metadata only. Secrets should be handled by backend or Key Vault flow.

## Stable error codes

| Code | Meaning |
|---|---|
| `UNAUTHENTICATED` | No valid user/session. |
| `FORBIDDEN` | User lacks permission. |
| `AI_SYSTEM_NOT_FOUND` | System does not exist or not visible. |
| `AI_SYSTEM_NOT_APPROVED` | System is pending/blocked/retired. |
| `PROMPT_VERSION_NOT_ACTIVE` | No active prompt version. |
| `POLICY_CHECK_FAILED` | Prompt/input failed policy. |
| `PII_REVIEW_REQUIRED` | PII requires review. |
| `EVALUATION_FAILED` | Output failed evaluator threshold. |
| `REVIEW_NOT_FOUND` | Review not found. |
| `INCIDENT_NOT_FOUND` | Incident not found. |
| `AUDIT_LOG_FAILURE` | Critical audit event could not be written. |
| `PROVIDER_UNAVAILABLE` | LLM/safety provider unavailable. |
| `RATE_LIMIT_EXCEEDED` | Request quota exceeded. |

## OpenAPI

FastAPI should expose generated OpenAPI at:

```text
/api/v1/openapi.json
/docs
```

Later, frontend TypeScript types can be generated from OpenAPI.
