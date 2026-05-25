# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-25  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


## Purpose

This document explains how the current local prototype becomes a practical organisational AI governance system.

The core point:

```text
The mock data is not the product.
The product is the governance operating model around AI execution.
```

We have already built the governed execution spine:

```text
AI app or user
  -> Governance Gateway
  -> policy decision
  -> approval check
  -> PII check
  -> provider call
  -> output PII check
  -> evaluation
  -> review routing
  -> incident creation
  -> audit events
  -> dashboard evidence
```

The next phase replaces demo edges with real organisational boundaries.

## What exists today

### AI systems registry

The registry answers:

- What AI systems exist?
- Who owns them?
- Which department is responsible?
- Which model/provider do they use?
- Are they approved?
- Do they process personal data?
- Are they high risk?

Example:

```text
Customer Support Summariser
Owner: Head of Support
Department: Customer Success
Model: llama3.2 / Azure OpenAI / OpenAI later
Risk: medium
Contains personal data: yes
Approval status: approved
Human oversight required: yes
```

### Governance gateway

Instead of applications calling an LLM directly:

```text
support app -> OpenAI
```

The target pattern is:

```text
support app -> AI Governance Control Tower -> approved provider
```

Every call goes through:

- System lookup.
- Approval status.
- Policy decision.
- Prompt and input evidence capture.
- PII detection.
- Provider execution.
- Output checks.
- Evaluation.
- Review/incident routing.
- Audit logging.

### Evidence and auditability

Every governed run can answer:

- Who or what asked?
- Which AI system was used?
- Which model provider was called?
- Which model/version answered?
- What prompt, input, output, and retrieved context were involved?
- Was PII detected?
- What policy decision was made?
- Which rules matched?
- Was the output evaluated?
- Did a human need to review it?
- Was an incident created?

That is the difference between AI usage and governed AI usage.

### Human review and incidents

Risky runs route to reviewers:

```text
Risk detected -> reviewer queue -> decision -> notes -> audit trail
```

Triggers include:

- PII detected in input.
- PII detected in output.
- Evaluation score below threshold.
- Hallucination flag.
- High-risk system requiring oversight.
- Later: policy violation, prompt injection, unapproved tool action.

## Why mock data remains

The mock data is scaffolding. It lets the governance workflow be built before real business integrations are available.

| Current mock/demo object | Real business equivalent |
|---|---|
| Demo AI systems | Real registered AI apps and use cases |
| Mock users/actors | SSO users, service accounts, teams, agents |
| Synthetic prompts | Real approved prompt versions |
| Synthetic input text | Real app/user input |
| Synthetic retrieved docs | CRM, Zendesk, SharePoint, Confluence, internal docs |
| Local Ollama | Azure OpenAI, OpenAI, Anthropic, local/private models |
| Local PII heuristics | Presidio, Azure AI Content Safety, DLP tools |
| Local evaluation | LLM-as-judge, Azure evals, custom policy evaluators |
| Mock cost estimate | Provider token/cost telemetry |
| Local audit events | Evidence ledger, audit exports, GRC integration |

This is the correct order: prove the governance path first, then replace synthetic edges with real integrations.

## Business fit

In an organisation, the Control Tower is the runtime governance layer between AI-consuming applications and model/tool providers.

Example flow:

```text
Customer support platform wants to summarise a ticket
  -> calls Control Tower
  -> Control Tower checks registry, approval, identity, prompt, PII, data source, policy
  -> calls approved provider
  -> evaluates output
  -> logs evidence
  -> routes risky output to review
```

The organisation gets:

- AI inventory.
- Runtime control.
- Evidence.
- Review workflow.
- Incident tracking.
- Audit trail.
- Provider visibility.
- Cost and usage visibility.

## What is missing for business use

### 1. Real identity and roles

Current actors are labels such as:

```text
local:ollama-test
```

A business needs:

- Microsoft Entra ID / SSO.
- Admin, analyst, reviewer, auditor.
- Service accounts.
- Agent identities.
- Department membership.
- Owner mappings.

This answers:

- Who asked?
- Were they allowed?
- What role did they have?
- Which department owned the action?

### 2. Real application integration

Today the frontend can manually call the gateway. A business needs internal applications to replace direct LLM calls with governed calls.

Target SDK/API shape:

```ts
await governance.run({
  ai_system_id,
  actor,
  prompt,
  input_text,
  retrieved_documents,
  metadata
});
```

This makes the Control Tower a runtime dependency for AI applications.

### 3. Real data-source governance

Today retrieved documents are passed as raw strings. A business needs registered data sources:

- Zendesk.
- Salesforce.
- SharePoint.
- Confluence.
- Google Drive.
- Internal policy docs.
- Vector stores.

The gateway should check:

- Is this AI system allowed to use this source?
- Is this user/agent allowed to access this document?
- Is the document sensitive?
- Was the source logged?

### 4. Prompt governance

Prompt governance now supports the core operational lifecycle:

- Draft prompt.
- Approve prompt.
- Activate prompt.
- Retire prompt.
- Audit prompt changes.
- Require gateway requests to use the active approved prompt exactly.

Still needed:

- Compare prompt versions.
- Add richer prompt approval evidence before activation.

### 5. Stronger safety and compliance checks

Current checks are useful prototype signals, not enterprise controls.

Next controls:

- Presidio / Microsoft Presidio.
- NER-based entity detection.
- Prompt injection detection.
- Jailbreak detection.
- Policy rules.
- Pre-LLM redaction.
- Output sanitisation.
- Provider safety APIs.

### 6. Real provider adapters

Ollama proves the provider boundary works. Next adapters should use the same interface:

- Ollama.
- OpenAI.
- Azure OpenAI.
- Anthropic.
- Local/private models.

The governance system should not care which provider sits behind the interface.

### 7. Business reporting

Governance, risk, security, compliance, and operations teams need:

- AI systems by department.
- Runs by system.
- Cost by model.
- Incidents by severity.
- Failed evaluations.
- Review backlog.
- High-risk systems.
- Approval status.
- Audit exports.

## Practical product shape

A business version should work like this:

1. Register every AI system.
2. Force every AI app to call the gateway.
3. Attach identity, role, department, ownership, and agent/service account context.
4. Log every run.
5. Evaluate every output.
6. Govern tool calls and agent capabilities.
7. Create incidents and reviews automatically.
8. Give auditors and governance teams searchable evidence.
9. Provide dashboards for risk, cost, usage, review backlog, and failures.

The Control Tower becomes an AI operations and governance layer, not a chatbot.

## Immediate build priorities

### 1. Gateway client and integration contract

- Publish a clean API contract.
- Add a small TypeScript or Python client.
- Make it easy for internal apps to call the gateway.

### 2. Actor and role model

- Add users, service accounts, agents, and roles.
- Store actor identity on model runs, tool calls, and audit events.
- Enforce admin, analyst, reviewer, and auditor permissions.

### 3. Data-source registry

- Register data sources.
- Link retrieved documents to approved sources.
- Add source and document permission checks.

### 4. Prompt governance

- Make prompt versions first-class in the UI.
- Require active prompt version for approved systems.
- Audit all prompt activation changes.
- Require governed runs to match the active approved prompt.

### 5. Provider settings page

- Show current provider: mock, Ollama, OpenAI, Azure.
- Add provider connectivity checks.
- Keep secrets backend-only.

### 6. Pre-LLM redaction and prompt injection detection

- Detect risky input before model execution.
- Redact personal data where policy requires it.
- Route suspicious prompt injection attempts to review or block.

### 7. Audit export

- Export runs, incidents, reviews, policy decisions, and audit events.
- Support auditor-friendly evidence packs.

## Near-term milestone

The next credible milestone is:

```text
An internal app can replace a direct LLM call with the Control Tower gateway,
using a registered AI system, a real actor identity, a governed prompt version,
registered retrieval sources, policy decisions, review routing, and audit evidence.
```

That is the point where the system stops being a demo dashboard and becomes a real governance gateway.

## Clean-mode operation

The local app can run without synthetic demo data.

Use:

```text
ENABLE_DEMO_SEED=false
```

This keeps migrations and the application shell active, but stops startup from creating demo AI systems and demo model runs. Register real organisational systems through the UI or API instead.

To remove existing demo seed records from a local database:

```bash
docker compose run --rm backend python -m app.cli clear-demo
```

To empty a non-production database that also contains earlier ad hoc test records:

```bash
docker compose run --rm backend python -m app.cli clear-all-local-data --confirm CLEAR_ALL_LOCAL_DATA
```

To re-add demo records for screenshots or demos:

```bash
docker compose run --rm backend python -m app.cli seed-demo
```

For the current product walkthrough, prefer:

```bash
docker compose run --rm backend python -m app.cli seed-showcase
```

This creates a customer support governance scenario plus sales, procurement, and blocked HR examples with active prompts, run history, evaluations, an incident, and a pending review.

Production must not run with `ENABLE_DEMO_SEED=true`, and the full local reset command is blocked when `APP_ENV=production`.
