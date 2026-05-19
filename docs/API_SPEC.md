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
    "Detailed model run persistence will be added in the model_runs episode."
  ]
}
```

Blocked response:

```json
{
  "run_id": null,
  "status": "blocked",
  "output_text": null,
  "governance_messages": [
    "Execution blocked because approval status is blocked.",
    "No model provider call was made."
  ]
}
```

Episode 3 gateway rules:

- Missing AI system returns `404` with `AI_SYSTEM_NOT_FOUND`.
- `approved` systems execute through `LocalMockLLMProvider`.
- `pending` systems return `requires_review` and do not execute.
- `blocked` and `retired` systems return `blocked` and do not execute.
- Gateway attempts create audit events with actions such as `governance.run.executed`, `governance.run.blocked`, and `governance.run.requires_review`.

## Data sources

### `GET /api/v1/data-sources`

Returns registered data sources.

### `POST /api/v1/data-sources`

Request:

```json
{
  "name": "Zendesk",
  "source_type": "support",
  "description": "Customer support tickets",
  "sensitivity": "personal"
}
```

## Prompt versions

### `POST /api/v1/ai-systems/{system_id}/prompt-versions`

Create draft prompt version.

Request:

```json
{
  "name": "Support summariser v2",
  "prompt_text": "Summarise the support ticket. Do not include payment data. If personal data is present, minimise it."
}
```

### `PATCH /api/v1/prompt-versions/{prompt_version_id}/activate`

Activate prompt version. Requires appropriate role.

## Governance gateway

### `POST /api/v1/governance/run`

Primary runtime endpoint.

Request:

```json
{
  "ai_system_id": "sys_001",
  "input_text": "Customer Sarah says her order did not arrive. Her email is sarah@example.test.",
  "prompt_override": null,
  "retrieval_request": {
    "enabled": true,
    "query": "refund policy delayed order",
    "max_documents": 3
  },
  "metadata": {
    "source_app": "support-console",
    "environment": "local-demo"
  }
}
```

Successful response:

```json
{
  "model_run_id": "run_001",
  "output_text": "The customer reports a missing order and requests support. Suggested next step: verify delivery status and provide refund or replacement options.",
  "route_decision": "allow_with_review",
  "route_reasons": [
    "Personal data detected in input",
    "System requires human oversight"
  ],
  "evaluation": {
    "overall_score": 82,
    "pii_detected": true,
    "pii_types": ["email"],
    "hallucination_flag": false,
    "requires_human_review": true
  },
  "review_id": "rev_001",
  "incident_id": null,
  "cost_usd": 0.0021,
  "latency_ms": 840
}
```

Blocked response:

```json
{
  "model_run_id": "run_002",
  "output_text": null,
  "route_decision": "block",
  "route_reasons": [
    "AI system approval status is blocked",
    "Model execution is not permitted"
  ],
  "review_id": null,
  "incident_id": "inc_001"
}
```

## Model runs

### `GET /api/v1/model-runs`

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

### `GET /api/v1/model-runs/{run_id}`

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

## Evaluations

### `GET /api/v1/evaluations/failed`

Returns failed or review-required evaluations.

### `GET /api/v1/model-runs/{run_id}/evaluation`

Returns evaluation result for a run.

## Human reviews

### `GET /api/v1/reviews`

Query params:

```text
status
risk_level
system_id
assigned_to
page
page_size
```

### `GET /api/v1/reviews/{review_id}`

Returns review detail including run evidence.

### `PATCH /api/v1/reviews/{review_id}/decision`

Request:

```json
{
  "decision": "approved",
  "notes": "Output is acceptable after confirming the email address is not included in the response.",
  "final_output_override": null
}
```

Response:

```json
{
  "id": "rev_001",
  "status": "completed",
  "decision": "approved",
  "completed_at": "2026-05-12T10:45:00Z"
}
```

## Incidents

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
  "severity": "medium",
  "resolution_notes": "Prompt updated to redact email addresses. Reviewer training note added."
}
```

## Audit logs

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
