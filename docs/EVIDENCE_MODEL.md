# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-19  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


# Evidence Model

## Purpose

This document defines how the AI Governance Control Tower should generate, store, link, export, and explain governance evidence.

The project thesis is:

> Policy defines intent. Engineering creates evidence.

The Control Tower should make evidence generation explicit. Every important governance claim should be backed by an object, event, record, or export.

## Evidence principles

### 1. Evidence over vibes

Scores, dashboards, and compliance language are not enough. Each governance claim should be traceable to evidence.

Example:

```text
Claim: This AI system was approved.
Evidence: approval status change event, actor, timestamp, before/after state, approval note.
```

### 2. Proportionality

Not every low-risk AI interaction needs the same level of evidence as a high-risk or sensitive workflow.

Evidence collection should depend on:

- System risk level.
- Data sensitivity.
- User role.
- Deployment environment.
- Potential impact.
- Applicable policies.
- Evaluation results.
- Route decision.

### 3. Privacy by design

Evidence should not become a new source of harm.

The system should:

- Avoid storing full prompts/outputs in generic audit logs.
- Store sensitive content in restricted records.
- Redact where possible.
- Support retention rules.
- Limit export access.
- Mark synthetic demo evidence clearly.
- Avoid using real user data in development or demos.

### 4. Explainability without false certainty

Evidence should show what checks were run and why decisions were made, but it should not imply the system detected every risk.

### 5. Append-only audit history

Normal app flows should not update or delete audit events. Corrections should create new events.

## Evidence object model

### Evidence item

An `evidence_item` is a linkable record that points to the thing supporting a governance claim.

Suggested fields:

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | Unique evidence ID |
| `company_id` | UUID | Tenant/company scope |
| `evidence_type` | enum | See evidence types below |
| `title` | string | Human-readable title |
| `summary` | string | Short explanation |
| `source_entity_type` | enum | `ai_system`, `model_run`, `evaluation_result`, `human_review`, `incident`, `audit_event`, `policy_version`, `control_test_result` |
| `source_entity_id` | UUID | Linked source record |
| `control_id` | string/null | Optional control catalogue ID |
| `framework_ref` | string/null | Optional NIST/EU/ISO/OECD/OWASP mapping |
| `risk_level` | enum | Low, Medium, High, Critical |
| `sensitivity` | enum | Public, Internal, Confidential, Restricted |
| `contains_personal_data` | bool | Whether evidence may include personal data |
| `redaction_status` | enum | Not needed, Redacted, Needs redaction, Restricted |
| `created_by` | UUID/system | Actor or system |
| `created_at` | timestamp | Immutable creation time |
| `metadata` | json | Tool-specific details |

### Evidence types

| Type | Description | Example source |
|---|---|---|
| `registration` | AI system inventory/registration evidence | `ai_system` |
| `approval` | Approval or lifecycle state evidence | `approval_status_changed` audit event |
| `policy_decision` | Policy/gateway decision evidence | `route_decision` |
| `model_run` | Runtime use evidence | `model_run` |
| `evaluation` | Pre/post evaluation evidence | `evaluation_result` |
| `human_review` | Human oversight evidence | `human_review` |
| `incident` | Incident and remediation evidence | `incident` |
| `audit` | Change/action history evidence | `audit_event` |
| `control_test` | Control effectiveness test evidence | `control_test_result` |
| `export` | Generated evidence pack/export | `evidence_pack` |
| `integration` | Provider/configuration evidence | `integration_status` |

## Core evidence chain

A governed run should create a chain like this:

```text
AI system registration
  -> owner assignment
  -> approval status
  -> prompt version
  -> gateway request
  -> pre-execution checks
  -> risk score
  -> route decision
  -> model output, if allowed
  -> post-execution evaluation
  -> human review, if required
  -> incident, if triggered
  -> audit events
  -> evidence item links
```

## Required evidence by workflow

### AI system registration

Minimum evidence:

- AI system created.
- Owner assigned.
- Department recorded.
- Intended use recorded.
- Data sources declared.
- Personal data flag recorded.
- Risk level set.
- Approval status set.
- Audit event created.

Evidence objects:

```text
ai_system
audit_event: ai_system.created
evidence_item: registration
```

### Approval change

Minimum evidence:

- Actor.
- Previous approval status.
- New approval status.
- Reason/note.
- Timestamp.
- Related system.
- Optional reviewer.

Evidence objects:

```text
audit_event: approval_status.changed
evidence_item: approval
```

### Governed model run

Minimum evidence:

- AI system ID.
- Prompt version ID.
- User/app identity.
- Timestamp.
- Provider/model.
- Pre-check results.
- Risk score and factors.
- Route decision.
- Model metadata if executed.
- Post-check results if executed.
- Evaluation result.
- Review/incident links if created.

Evidence objects:

```text
model_run
evaluation_result
route_decision
audit_event
evidence_item: model_run
evidence_item: evaluation
```

### Human review

Minimum evidence:

- Reviewer.
- Review item.
- Reason for review.
- Decision.
- Rationale.
- Timestamp.
- Linked model run/evaluation.
- Escalation or remediation action.

Evidence objects:

```text
human_review
audit_event: review.decision
evidence_item: human_review
```

### Incident

Minimum evidence:

- Category.
- Severity.
- Source model run or review.
- Detection method.
- Owner.
- Status.
- Investigation notes.
- Remediation.
- Resolution/dismissal reason.
- Related approval status changes.

Evidence objects:

```text
incident
audit_event: incident.created/status_changed
evidence_item: incident
```

## Suggested database additions

### `evidence_items`

```sql
CREATE TABLE evidence_items (
    id UUID PRIMARY KEY,
    company_id UUID NOT NULL,
    evidence_type TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    source_entity_type TEXT NOT NULL,
    source_entity_id UUID NOT NULL,
    control_id TEXT,
    framework_ref TEXT,
    risk_level TEXT,
    sensitivity TEXT NOT NULL DEFAULT 'internal',
    contains_personal_data BOOLEAN NOT NULL DEFAULT false,
    redaction_status TEXT NOT NULL DEFAULT 'not_needed',
    created_by UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB NOT NULL DEFAULT '{}'
);
```

### `evidence_packs`

```sql
CREATE TABLE evidence_packs (
    id UUID PRIMARY KEY,
    company_id UUID NOT NULL,
    title TEXT NOT NULL,
    scope_type TEXT NOT NULL,
    scope_id UUID,
    date_from TIMESTAMPTZ,
    date_to TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'draft',
    created_by UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    exported_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'
);
```

### `evidence_pack_items`

```sql
CREATE TABLE evidence_pack_items (
    id UUID PRIMARY KEY,
    evidence_pack_id UUID NOT NULL REFERENCES evidence_packs(id),
    evidence_item_id UUID NOT NULL REFERENCES evidence_items(id),
    sort_order INTEGER NOT NULL DEFAULT 0
);
```

## Evidence pack types

| Evidence pack | Purpose |
|---|---|
| AI system pack | Show registration, ownership, approval, runs, evals, incidents for one system |
| Incident pack | Show complete chain around an incident |
| Control pack | Show where a specific control operated and whether it passed |
| Framework mapping pack | Show evidence linked to NIST/EU/ISO/OECD concepts |
| Review-period pack | Show activity over a defined period |
| Demo pack | Show synthetic evidence for YouTube/stakeholder walkthroughs |

## Evidence pack example

```json
{
  "title": "Customer Support Summariser - Governance Evidence Pack",
  "scope_type": "ai_system",
  "scope_id": "system_customer_support_summariser",
  "date_from": "2026-05-01T00:00:00Z",
  "date_to": "2026-05-31T23:59:59Z",
  "items": [
    {
      "evidence_type": "registration",
      "title": "System registered",
      "source_entity_type": "ai_system"
    },
    {
      "evidence_type": "approval",
      "title": "System approved for medium-risk customer support use",
      "source_entity_type": "audit_event"
    },
    {
      "evidence_type": "evaluation",
      "title": "Output PII check failed on run 184",
      "source_entity_type": "evaluation_result"
    },
    {
      "evidence_type": "human_review",
      "title": "Reviewer rejected flagged output",
      "source_entity_type": "human_review"
    },
    {
      "evidence_type": "incident",
      "title": "PII exposure incident resolved",
      "source_entity_type": "incident"
    }
  ]
}
```

## Redaction and sensitivity

### Sensitivity levels

| Level | Meaning | Example |
|---|---|---|
| Public | Safe to include in public demos/docs | Synthetic demo data |
| Internal | General internal evidence | System metadata |
| Confidential | Restricted business or user data | Prompt/output excerpts |
| Restricted | Sensitive personal, regulated, legal, HR, security data | PII incident detail |

### Redaction rules

| Content | Default handling |
|---|---|
| Full prompt | Restricted unless synthetic |
| Full output | Restricted unless synthetic |
| Email addresses | Redact in exports by default |
| Phone numbers | Redact in exports by default |
| Names | Redact if personal data context |
| Customer IDs | Hash or partially mask |
| Access tokens/secrets | Never store; block and incident |
| System prompts | Restricted |
| Retrieved documents | Store references/snippets, not full docs by default |

## Evidence quality levels

Not all evidence is equal. Add a quality indicator where useful.

| Level | Meaning |
|---|---|
| `system_generated` | Created automatically by application logic |
| `human_attested` | Added or confirmed by a human reviewer |
| `externally_verified` | Validated by external tool, auditor, or provider |
| `synthetic_demo` | Demo evidence only, not real governance evidence |

## Control-to-evidence mapping

Each control should produce predictable evidence.

| Control | Evidence |
|---|---|
| ACT-REG-001 | `ai_system`, `audit_event`, `evidence_item` |
| ACT-APP-001 | `route_decision`, `blocked_model_run`, `audit_event` |
| ACT-GW-001 | `model_run`, `evaluation_result`, `audit_event` |
| ACT-RISK-001 | `risk_score`, `risk_score_breakdown` |
| ACT-EVAL-001 | `input_pii_flag`, `evaluation_result` |
| ACT-REV-001 | `human_review`, `review_reason` |
| ACT-INC-001 | `incident`, `incident_category`, `severity` |
| ACT-AUD-001 | `audit_event` |
| ACT-POL-001 | `policy_version`, `policy_version_used` |

## Evidence export API sketch

```text
POST /api/v1/evidence-packs
GET /api/v1/evidence-packs
GET /api/v1/evidence-packs/{pack_id}
POST /api/v1/evidence-packs/{pack_id}/items
POST /api/v1/evidence-packs/{pack_id}/export
```

Example request:

```json
{
  "title": "May AI Governance Review",
  "scope_type": "review_period",
  "date_from": "2026-05-01T00:00:00Z",
  "date_to": "2026-05-31T23:59:59Z",
  "filters": {
    "risk_levels": ["medium", "high"],
    "include_incidents": true,
    "include_reviews": true,
    "redaction_mode": "standard"
  }
}
```

## Evidence dashboard

The dashboard should show:

- Evidence generated this period.
- Evidence by type.
- Evidence by system.
- Evidence by framework mapping.
- Evidence by control.
- Evidence gaps.
- High-risk systems without recent evidence.
- Incidents without remediation evidence.
- Systems with stale approvals.
- Reviews past SLA.

## Evidence gaps

The system should surface missing evidence, not hide it.

Examples:

| Gap | Meaning |
|---|---|
| No owner | AI system lacks accountability |
| No approval event | Approval status exists but history is missing |
| No evaluation record | Runs exist without checks |
| No review decision | Risky output was routed but not resolved |
| No remediation | Incident was closed without corrective evidence |
| No policy version | Route decision cannot be tied to rule state |
| No data source declaration | System context is incomplete |

## Public wording guidance

Use:

> The Control Tower generates operational evidence for AI governance decisions.

Avoid:

> The Control Tower proves compliance.

Use:

> Evidence can support audits, internal reviews, assurance conversations, and accountability.

Avoid:

> Evidence automatically satisfies legal or certification requirements.

## MVP implementation recommendation

For MVP, implement evidence indirectly first:

- Ensure `model_run`, `evaluation_result`, `human_review`, `incident`, and `audit_event` records are strong.
- Add `evidence_item` later as a linking layer.
- Add evidence packs after the demo workflow is stable.

This avoids overengineering while preserving the evidence-first architecture.
