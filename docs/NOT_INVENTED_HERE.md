# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-19  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


# Not Invented Here Policy

## Purpose

This document prevents the project from becoming an overbuilt clone of existing tools.

The Control Tower should build the minimum custom functionality required to demonstrate runtime AI governance, then integrate or reference mature tools where appropriate.

## Core principle

> Build the governance workflow. Do not rebuild the entire AI tooling ecosystem.

The project's value is in connecting:

```text
inventory
  -> approval
  -> gateway
  -> checks
  -> route decision
  -> human review
  -> incident
  -> evidence
```

It is not in becoming the best standalone product for every category.

## What we should build ourselves

### 1. Governance gateway orchestration

Reason: This is the core product thesis.

Build:

- `POST /api/v1/governance/run`
- Pre-execution checks
- Route decision
- Model provider call
- Post-execution checks
- Review/incident routing
- Audit logging
- Governance metadata response

Do not outsource this whole flow because it is the reference implementation.

### 2. AI system registry

Reason: Governance needs ownership, purpose, risk, and data context.

Build:

- AI systems.
- Owners.
- Departments.
- Risk levels.
- Data-source declarations.
- Approval states.
- Prompt versions.
- Lifecycle state.

### 3. Human review workflow

Reason: Human oversight is central to governance and needs to be visible in the demo.

Build:

- Review queue.
- Review detail.
- Approve/reject/escalate/request changes.
- Reviewer rationale.
- Review audit event.

### 4. Incident workflow

Reason: Governance must show what happens when controls fail.

Build:

- Incident creation.
- Incident categories.
- Severity.
- Owner.
- Status lifecycle.
- Remediation notes.
- Links to runs, evals, and reviews.

### 5. Audit and evidence linking

Reason: Evidence is the differentiator.

Build:

- Append-only audit events.
- Evidence links.
- Evidence exports.
- Route reason history.
- Review/incident evidence chains.

### 6. Local MVP evaluators

Reason: The demo must run locally without external services.

Build simple versions of:

- PII detection.
- Prompt injection detection.
- Output safety flagging.
- Groundedness heuristic.
- Relevance heuristic.
- Cost/latency thresholds.

But every local evaluator should clearly state its limitations.

## What we should not overbuild

### 1. Full LLM observability platform

Do not rebuild Langfuse, Phoenix, or OpenTelemetry.

Build only enough to store model runs and governance metadata.

Later:

- Link to Langfuse traces.
- Emit OpenTelemetry spans.
- Integrate with Azure Monitor/Application Insights.

### 2. Full evaluation benchmark suite

Do not rebuild Inspect, Dioptra, Promptfoo, Giskard, Garak, or Ragas.

Build a provider interface and simple local checks.

Later:

- Run external eval suites.
- Store normalised results.
- Link results to evidence.

### 3. Full enterprise GRC platform

Do not rebuild complete vendor risk, policy management, audit workflows, controls testing, certifications, and enterprise reporting.

Build:

- AI-focused controls.
- Evidence chains.
- System-level governance.

Later:

- Integrate with GRC tools.
- Export evidence packs.

### 4. Full policy-as-code engine

Do not create a complex custom policy language.

Build:

- Python-based rule engine for MVP.
- Policy version records later.
- Provider interface for OPA or similar.

### 5. Full privacy/data governance platform

Do not rebuild Microsoft Purview, Collibra, BigID, OneTrust, or equivalent data governance tools.

Build:

- Data-source metadata.
- Sensitivity labels.
- Personal data flags.
- Provider interface.

Later:

- Integrate with data catalogues.

### 6. Full identity platform

Do not build authentication/identity from scratch beyond local mock users.

Build:

- Local mock users.
- Roles.
- Permissions for demo.

Later:

- Microsoft Entra ID.
- SSO.
- SCIM/group mapping.

### 7. Full model registry / MLOps platform

Do not rebuild MLflow, model registries, deployment systems, or feature stores.

Build:

- Provider/model metadata.
- Prompt versions.
- Run records.
- Risk metadata.

Later:

- Integrate with model registries.

## Decision rubric

Before building a feature, ask:

| Question | If yes | If no |
|---|---|---|
| Is this required to demonstrate the governance workflow? | Build minimal version | Consider integration only |
| Does this generate governance evidence? | Build or link evidence | Avoid in MVP |
| Is there a mature open-source tool already? | Integrate later | Build if essential |
| Is this specific to AI governance routing/review/incidents? | Build | Avoid overbuilding |
| Would this make the demo clearer? | Build simple version | Defer |
| Would this create false confidence? | Add limitation or defer | Continue |
| Can this run locally with synthetic data? | Good MVP candidate | Defer or stub |

## Build/integrate/defer matrix

| Capability | Decision | Reason |
|---|---|---|
| Registry | Build | Core governance context |
| Approval workflow | Build | Core governance control |
| Gateway | Build | Core differentiator |
| Risk scoring | Build simple | Needed for routing; configurable |
| Local PII check | Build simple | Local demo requirement |
| Advanced PII detection | Integrate | Better handled by specialised tools |
| Prompt injection heuristic | Build simple | Local demo requirement |
| Advanced red-teaming | Integrate | Use Garak/Promptfoo/Giskard/etc. |
| Groundedness heuristic | Build simple | Demo requirement |
| Advanced RAG eval | Integrate | Use Ragas/other eval tools |
| Full tracing | Integrate | Use Langfuse/Phoenix/OpenTelemetry |
| Audit logs | Build | Core evidence layer |
| Evidence packs | Build later | Strong differentiator |
| Policy-as-code | Integrate later | OPA already exists |
| SSO | Integrate later | Use Entra/Auth providers |
| Cloud secrets | Integrate later | Use Key Vault/secrets managers |
| Data catalogue | Integrate later | Use Purview/equivalent |
| Enterprise certification workflow | Defer | Out of scope for MVP |

## MVP feature boundary

The MVP should prove this sentence:

> A model request can move through a governed runtime path where the system checks approval, detects risk, routes the output, records evidence, and shows the result in a control tower.

If a feature does not support that sentence, it can probably wait.

## Integration-first architecture

All specialised functions should sit behind interfaces:

```text
LLMProvider
SafetyProvider
GroundednessProvider
EvaluationProvider
PolicyDecisionProvider
TelemetryProvider
SecretManager
IdentityProvider
DataGovernanceProvider
```

Benefits:

- Keeps MVP simple.
- Avoids vendor lock-in.
- Enables Azure-aware architecture.
- Lets other tools plug into the Control Tower.
- Makes the project easier to explain.

## Public wording guidance

Use:

> We are not trying to rebuild every AI governance tool. We are building the runtime control-and-evidence layer that can connect them.

Avoid:

> We are building the one platform that replaces all AI governance tools.

Use:

> The MVP uses simple local evaluators so the whole workflow can be demonstrated without external services.

Avoid:

> Our MVP checks are production-grade safety systems.

Use:

> The architecture is designed to integrate stronger tools once the governance flow is proven.

Avoid:

> We will solve every part of AI governance ourselves.

## Anti-patterns to avoid

### Anti-pattern 1 — Dashboard-first governance

A pretty dashboard without runtime controls is weak.

Avoid building metrics screens before the gateway, routes, reviews, and evidence records work.

### Anti-pattern 2 — Compliance theatre

Do not add framework badges, scores, or compliance claims without evidence and limitations.

### Anti-pattern 3 — Eval overconfidence

Do not treat a passing heuristic eval as proof of safety.

### Anti-pattern 4 — Human review as a checkbox

Human review must include context, rationale, decision, and audit trail.

### Anti-pattern 5 — Logs as governance

Logging is necessary but not sufficient. Governance also needs controls, escalation, and accountability.

### Anti-pattern 6 — Local demo with real sensitive data

Use synthetic data only.

### Anti-pattern 7 — Blocking everything

The system should be risk-based and proportional. Low-risk workflows should not be governed like critical workflows.

## Contribution guidance

When adding features, contributors should state:

```text
What governance risk does this address?
What control does it implement?
What evidence does it generate?
What existing tool could do this better?
Why should this be built here?
What are the limitations?
```

## Example feature decision

Feature request:

> Add advanced prompt red-teaming.

Decision:

- Do not build a full red-team suite in MVP.
- Add a provider interface.
- Add a simple prompt-injection heuristic for local demo.
- Later integrate Promptfoo/Garak/Giskard.
- Store external red-team output as `control_test_result` and `evidence_item`.

Reason:

> Red-teaming is important, but the Control Tower's core value is routing findings into governance actions and evidence, not replacing specialised scanners.

## Final rule

When in doubt:

> Build the part that turns a signal into governance action and evidence. Integrate the part that produces the specialised signal.
