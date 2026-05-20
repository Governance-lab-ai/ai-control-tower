# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-12  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


## Testing objective

Testing should prove that the core governance workflow is reliable, explainable, and secure enough for a public prototype.

The most important tests are not generic UI tests. They are tests that prevent governance bypass.

## Test pyramid

```text
             E2E demo journeys
          Integration API tests
       Service and policy unit tests
  Static checks, linting, type checks, security scans
```

## Backend unit tests

### Risk engine

Test cases:

- Low-risk approved system routes to allow.
- Medium-risk approved system with PII routes to review.
- High-risk system routes to hold for review.
- Blocked system routes to block.
- Pending system routes to block/hold depending policy.
- Prompt injection signal increases route severity.
- Missing safety result defaults to review for medium/high systems.

### Approval gate

Test cases:

- Approved systems can execute.
- Pending systems cannot execute.
- Blocked systems cannot execute.
- Retired systems cannot execute.
- Approval status changes generate audit events.

### PII detector

Test cases:

- Email detected.
- Phone detected.
- Payment card-like pattern detected.
- False-positive handling for harmless numbers.
- Redacted preview does not expose full value.

### Evaluation service

Test cases:

- Every executed gateway run queues one evaluation.
- Output unsupported by retrieved docs lowers groundedness score.
- Low scores route medium/high/critical systems to review according to thresholds.
- Hallucination flags route runs to review.
- Safe, relevant output passes.
- Failed evaluations appear through `/evaluations?failed_only=true`.

### Human review service

Test cases:

- PII detected in input creates a pending human review item.
- PII detected in output creates a pending human review item.
- Failed evaluation or hallucination flag creates a pending human review item.
- High-risk systems with human oversight required create a pending human review item.
- Run-specific incident lookup returns incidents linked to the reviewed model run.
- Reviewer can approve, reject, or escalate a pending review with notes.
- Decided reviews cannot be decided a second time.
- Reviewer decisions create audit events.

### Audit logger

Test cases:

- Critical action creates audit event.
- Sensitive fields are redacted.
- Audit failure behaviour is correct.

## Backend integration tests

### Governance run happy path

1. Create approved AI system.
2. Create active prompt version.
3. Submit run request.
4. Assert model run created.
5. Assert evaluation created.
6. Assert audit event created.
7. Assert response includes route metadata.

### Blocked system path

1. Create blocked AI system.
2. Submit run request.
3. Assert no LLM provider call.
4. Assert blocked model run shell or blocked audit event exists.
5. Assert response route is `block`.

### Review path

1. Submit request with PII.
2. Assert review item created.
3. Approve review.
4. Assert review status is `approved`.
5. Assert audit event exists.

### Incident path

1. Submit request that triggers severe PII output or jailbreak.
2. Assert incident created.
3. Update incident to resolved.
4. Assert audit events exist.

## Frontend tests

### Component tests

- Risk badge renders correct label and accessible text.
- Approval badge renders correct label and accessible text.
- Metric card handles loading/empty/error.
- Risk heatmap renders values and tooltips.
- Review action buttons require confirmation for reject/escalate.
- Incident table filters correctly.

### Page tests

- Dashboard loads summary panels.
- Registry table displays systems and filters.
- System detail tabs render.
- Review queue displays pending items.
- Audit log supports filters.

### Accessibility tests

- Keyboard navigation works for main nav and review actions.
- Focus states visible.
- Colour is not the only status indicator.
- Charts include text summaries.

## E2E tests with Playwright

### Demo journey 1 — Register and approve a system

1. Open dashboard.
2. Go to AI Systems.
3. Register Customer Support Summariser.
4. Confirm status is pending.
5. Approve system.
6. Confirm audit log event.

### Demo journey 2 — Run governed AI request

1. Go to system detail.
2. Submit run.
3. See output/evaluation.
4. Confirm model run appears in run history.

### Demo journey 3 — PII review

1. Submit prompt with synthetic email/payment pattern.
2. Confirm review item created.
3. Open review queue.
4. Approve/reject.
5. Confirm audit log.

### Demo journey 4 — Incident

1. Trigger policy violation or PII exposure.
2. Confirm incident appears.
3. Resolve incident.
4. Confirm dashboard updates.

## Security tests

- Unauthorised user cannot approve systems.
- Viewer cannot view full prompt/output for sensitive run.
- Reviewer can view assigned review.
- Export endpoint requires elevated role.
- API rejects oversized prompt/input.
- API rejects invalid enum values.
- Frontend does not contain provider API keys.
- Model output is escaped and cannot inject script.

## Mock provider tests

Use mock providers to make tests deterministic.

Mock LLM outputs:

- Safe output.
- Output with email.
- Output with hallucinated claim.
- Output with policy violation.
- Timeout/error.

Mock safety results:

- Passed.
- PII detected.
- Prompt injection detected.
- Provider unavailable.

## Test data principles

- Synthetic only.
- Use `.test` domains for fake emails.
- Mark fake payment/card data clearly as synthetic.
- Do not use real names from public figures.
- Avoid realistic personal addresses unless clearly fake.

## CI requirements

Run on every PR:

- Backend lint.
- Backend tests.
- Frontend lint.
- Frontend typecheck.
- Frontend tests.
- Optional E2E smoke test.
- Secret scan.

## MVP test acceptance criteria

- All core backend services have unit tests.
- Gateway has integration tests for allow/block/review/incident paths.
- Dashboard has at least smoke tests.
- Review queue has E2E coverage.
- CI fails if tests fail.
- Tests can run without Azure credentials.
