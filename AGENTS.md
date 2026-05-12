# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-12  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


## Purpose of this document

This document serves two purposes:

1. **Instructions for development agents** such as coding assistants, automated code generators, and reviewers working in this repository.
2. **Product agent/service definitions** for the governance-related services inside the application.

## Part 1 — Instructions for development agents

### Project context

You are working on a local-first, Azure-aware AI Governance Control Tower.

The application should help organisations register, monitor, evaluate, review, and audit AI systems. It is not a generic chatbot app. It is the governance layer around AI apps.

### Non-negotiables

Do not:

- Hard-code secrets, API keys, tenant IDs, or connection strings.
- Put LLM API calls in frontend code.
- Use real personal data in seed data, screenshots, tests, or demos.
- Remove audit logging to simplify implementation.
- Bypass approval checks in the governance gateway.
- Create direct model execution endpoints that do not log runs.
- Claim legal or regulatory compliance.
- Treat local heuristic checks as definitive safety/compliance guarantees.
- Store full prompts/outputs in general application logs.

Always:

- Keep local providers and Azure providers behind interfaces.
- Add or update tests when changing routing, risk, evaluation, or review logic.
- Update relevant docs when changing architecture, API, schema, or security behaviour.
- Use typed schemas at boundaries.
- Keep route handlers thin and business logic in services.
- Preserve auditability.
- Prefer explicit, explainable decisions over hidden magic.

### Coding standards

Backend:

- FastAPI route handlers should call service classes.
- Pydantic models define request/response contracts.
- SQLAlchemy models define persistence only.
- Alembic migrations are required for schema changes.
- Use dependency injection for DB sessions and providers.
- Centralise configuration in `backend/app/core/config.py`.
- Use stable error codes.

Frontend:

- Use TypeScript strict mode.
- Keep API types in `frontend/lib/types.ts` or generated from OpenAPI later.
- Use design tokens from `DESIGN.md`.
- Keep components composable and accessible.
- Do not invent new colours without updating `DESIGN.md`.
- Use server-side fetching where appropriate, but protect sensitive actions.

Testing:

- Unit-test risk routing and evaluation rules.
- Integration-test API flows.
- Use synthetic fixtures only.
- Add Playwright smoke tests for the core demo journey.

### Important project flows

Core flow:

```text
Register system → approve/pending/block → run through gateway → checks → model call → evaluations → review/incident/audit → dashboard
```

Never implement a model run path that skips:

- System approval check.
- Prompt/input check.
- Logging.
- Evaluation creation.
- Audit event creation.

### Safe assumptions

Development agents may assume:

- The first company is `Acme Corp`.
- Local demo mode uses synthetic data.
- The app has mocked users until real auth is implemented.
- Azure integrations are optional until Phase 6.
- The product is a prototype inspired by governance practices, not a compliance product.

### Required response when uncertain

When a development agent is uncertain, prefer:

1. A small, typed, testable implementation.
2. A clear TODO comment.
3. A doc update noting the open decision.

Do not silently pick insecure defaults.

## Part 2 — Product agent/service definitions

The platform may contain several “agent-like” services. These are not autonomous agents making unsupervised decisions. They are bounded services with explicit inputs, outputs, and audit trails.

### 1. Registry Agent

**Purpose:** validate and enrich AI system registration.

Inputs:

- System name.
- Department.
- Owner.
- Model.
- Data sources.
- Personal data flag.
- Human oversight flag.

Outputs:

- Registry completeness score.
- Missing fields.
- Suggested risk questions.
- Audit event.

Boundaries:

- Cannot approve a system automatically in MVP.
- Cannot infer legal classification as fact.

### 2. Risk Assessment Agent

**Purpose:** calculate a dynamic risk score and recommended route.

Inputs:

- System risk level.
- Data sensitivity.
- User role.
- Prompt policy result.
- PII result.
- Retrieval context.
- Model type.
- Department.

Outputs:

- Risk score.
- Risk reasons.
- Route recommendation: allow, allow with review, hold, block.

Boundaries:

- Produces recommendations and route decisions according to configured policy.
- Must explain reasons.
- High-impact decisions should require human review.

### 3. Prompt Policy Agent

**Purpose:** inspect prompts and inputs before model execution.

Checks:

- Prompt injection patterns.
- Jailbreak language.
- Disallowed topics.
- Restricted data requests.
- Direct requests to reveal system prompt or hidden instructions.
- Suspicious tool-use instructions.

Outputs:

- Passed/failed.
- Severity.
- Categories.
- Explanation.

Boundaries:

- Does not replace model safety services.
- Should be conservative when attached to high-risk systems.

### 4. PII Detection Agent

**Purpose:** detect and classify personal data in inputs and outputs.

MVP checks:

- Email addresses.
- Phone numbers.
- Payment card-like patterns.
- National ID-like patterns.
- Addresses.
- Names only when paired with other sensitive indicators.

Outputs:

- PII detected boolean.
- PII types.
- Redacted preview.
- Severity.

Boundaries:

- Avoid storing detected values in audit logs.
- Store redacted snippets where possible.
- Local heuristics are not perfect.

### 5. Retrieval Governance Agent

**Purpose:** ensure retrieved documents are allowed for the system and user.

Checks:

- Data source is registered.
- System has permission to use the data source.
- User role is allowed.
- Document sensitivity is compatible with system approval.
- Retrieved document metadata is logged.

Outputs:

- Allowed docs.
- Blocked docs.
- Reasons.

Boundaries:

- MVP can use mocked retrieved documents.
- Later integrations may use product docs, Zendesk, CRM, or vector stores.

### 6. Evaluation Agent

**Purpose:** evaluate model output after execution.

Checks:

- Output safety.
- PII leakage.
- Groundedness against retrieved docs.
- Relevance to input.
- Factual consistency heuristic.
- Policy violations.

Outputs:

- Evaluation score.
- Per-check scores.
- Pass/fail.
- Review required boolean.
- Explanation.

Boundaries:

- Should not claim to prove truth.
- Should show evidence and uncertainty.

### 7. Review Routing Agent

**Purpose:** decide whether a model run needs human review.

Inputs:

- System risk level.
- Evaluation score.
- PII detection.
- Hallucination/groundedness flag.
- Prompt injection flag.
- Policy violation flag.

Outputs:

- Review required boolean.
- Assigned queue.
- Priority.
- Review reason.

Boundaries:

- Cannot auto-approve high-risk rejected items.
- All route decisions must be logged.

### 8. Incident Agent

**Purpose:** create and classify incident records when policy thresholds are crossed.

Incident types:

- PII exposure.
- Hallucination.
- Policy violation.
- Jailbreak attempt.
- Unapproved system use.
- Data leakage.
- Excessive cost/usage anomaly.

Outputs:

- Incident record.
- Severity.
- Owner.
- Linked run.
- Recommended next action.

Boundaries:

- Does not notify external systems in MVP unless explicitly configured.
- Does not delete or alter evidence.

### 9. Audit Agent

**Purpose:** ensure every important event produces an audit record.

Events:

- System created/updated.
- Approval status changed.
- Prompt version changed.
- Model run created.
- Evaluation failed.
- Review decision made.
- Incident opened/updated/resolved.
- Export generated.
- Integration setting changed.

Outputs:

- Append-only audit event.

Boundaries:

- Must minimise sensitive content in audit logs.
- Must be resilient; if audit logging fails, the main action should fail or be clearly marked depending on severity.

### 10. Cost and Usage Agent

**Purpose:** aggregate model usage and cost.

Inputs:

- Model runs.
- Tokens.
- Latency.
- Provider/model version.
- Cost estimates.

Outputs:

- Cost by system.
- Cost by department.
- Cost by model.
- Usage anomalies.

Boundaries:

- Costs may be estimates unless provider invoices are integrated.

## Agent observability

Each agent-like service should emit:

- Start/end timestamp.
- Input metadata, not sensitive values.
- Decision/result.
- Error details if safe.
- Linked model run ID.
- Linked audit event ID where relevant.

## Agent failure behaviour

| Service | Failure behaviour |
|---|---|
| Registry Agent | Return validation error; do not create incomplete critical records. |
| Risk Assessment Agent | Default to safer route: hold for review. |
| Prompt Policy Agent | For high-risk systems, hold/block; for low-risk, mark degraded and review. |
| PII Detection Agent | Default to review when unavailable. |
| Evaluation Agent | Mark evaluation incomplete and route to review. |
| Audit Agent | Fail critical state changes if audit cannot be recorded. |
| Cost Agent | Allow run but mark cost as unknown. |

## Agent prompt policy

If LLM-based evaluators are later added:

- They must not receive unnecessary sensitive data.
- Their prompts must be versioned.
- Their outputs must be treated as advisory signals.
- Their own model runs must be logged.
- They must be evaluated for consistency.
- They must not be allowed to silently change system approval states.
