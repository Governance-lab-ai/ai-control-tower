# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-12  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


## Governance model objective

The governance model defines how the system decides whether AI use is visible, approved, safe enough to run, routed to review, blocked, or escalated as an incident.

The model should be explainable and conservative. It should generate evidence, not false certainty.

## Governance principles

- **Visibility:** every AI system should be registered.
- **Ownership:** every system needs an accountable owner.
- **Approval:** risky systems should not run without approval.
- **Data awareness:** systems using personal or sensitive data need stronger controls.
- **Human oversight:** risky or uncertain outputs route to people.
- **Auditability:** decisions and changes are recorded.
- **Proportionality:** low-risk systems should not be governed like high-risk systems.
- **Evidence over vibes:** scores should be backed by reasons and metadata.

## AI system registration questions

Minimum fields:

- System name.
- Description.
- Department.
- Owner.
- Model provider/name.
- Data sources.
- Contains personal data?
- Intended users.
- Human oversight required?
- Risk level.
- Approval status.

Optional later fields:

- Intended purpose.
- Prohibited uses.
- Impacted stakeholders.
- Data retention period.
- Evaluation schedule.
- Monitoring owner.
- Legal/business reviewer.
- Deployment environment.

## Risk level rubric

### Low risk

Examples:

- Internal summarisation of non-sensitive public/internal docs.
- Drafting marketing copy with human review.
- Non-decision-support productivity assistant.

Controls:

- Registry required.
- Logging required.
- Basic checks.
- Review only on failed evaluations.

### Medium risk

Examples:

- Customer support summarisation.
- Sales email drafting using CRM context.
- Internal analytics assistant with confidential data.

Controls:

- Approval required.
- Personal data check.
- Human review for flagged outputs.
- Incident creation for PII leakage or hallucination.

### High risk

Examples:

- HR screening support.
- Finance decision support.
- Healthcare, legal, or regulated workflows.
- Systems influencing access, eligibility, or significant decisions.

Controls:

- Approval required.
- Human oversight required.
- Stricter thresholds.
- Outputs may be held before release.
- Stronger audit/export controls.

### Critical risk

Examples:

- Automated high-impact decisions without human oversight.
- Use of restricted data without controls.
- Safety-critical workflows.

Controls:

- Block by default in MVP.
- Governance admin review required.
- No direct output release.

## Approval workflow

```mermaid
stateDiagram-v2
  [*] --> Pending
  Pending --> Approved: Governance admin approves
  Pending --> NeedsChanges: Reviewer requests changes
  NeedsChanges --> Pending: Owner updates system
  Approved --> Blocked: Incident/policy change
  Approved --> Retired: Owner retires system
  Blocked --> Pending: Remediation submitted
  Retired --> [*]
```

Approval statuses:

| Status | Meaning |
|---|---|
| `pending` | Registered but not approved for use. |
| `approved` | Allowed to execute under defined controls. |
| `blocked` | Not allowed to execute. |
| `needs_changes` | Registration/prompt/policy must be updated. |
| `retired` | No longer active. |

## Governance gateway policy

The gateway evaluates:

- System approval state.
- System risk level.
- User role and department.
- Prompt version status.
- Personal data declaration.
- Data source permissions.
- Prompt/input policy checks.
- PII in input.
- Prompt injection/jailbreak signal.
- Retrieval document sensitivity.
- Provider availability.

Planned control services:

- PII detection using Microsoft Presidio/Presidio where available, plus regex, NER, and entity detection fallback.
- Prompt injection detection covering jailbreak attempts, suspicious prompt heuristics, and tool restriction logic.
- Redaction before LLM execution for names, emails, phone numbers, and account numbers.
- Role-based access for admin, analyst, reviewer, and auditor workflows.
- Audit capture for prompts, outputs, retrieved docs, approvals, costs, and reviewer actions.

Route decisions:

```text
allow
allow_with_review
hold_for_review
block
```

### Episode 3 and 4 local gateway rules

Episode 3 implements the first runtime gateway at `POST /governance/run`. Episode 4 adds persistent run logging for executed calls.

| Approval status | Gateway status | Execution behaviour |
|---|---|---|
| `approved` | `executed` | Calls `LocalMockLLMProvider` and returns mock output. |
| `pending` | `requires_review` | Does not execute. A model-run shell and governance audit event are recorded. |
| `blocked` | `blocked` | Does not execute. A model-run shell and governance audit event are recorded. |
| `retired` | `blocked` | Does not execute. A model-run shell and governance audit event are recorded. |
| missing system | HTTP 404 | Returns `AI_SYSTEM_NOT_FOUND`. |

Provider boundary:

- `LLMProvider` is the backend interface for model execution.
- `LocalMockLLMProvider` is the only active Episode 3 implementation.
- `AzureOpenAIProvider` is a placeholder and must not require credentials until the Azure integration phase.

Audit behaviour:

- Executed gateway calls record `governance.run.executed`.
- Blocked calls record `governance.run.blocked`.
- Pending calls record `governance.run.requires_review`.
- Executed calls create `model_runs` records with prompt, input, output, provider metadata, latency, mock cost, and status.
- Supplied retrieved documents are stored as `retrieved_documents` linked to the model run.
- Blocked and pending calls create model-run shell records with no output, zero cost, zero latency, and `model_version` set to `not_executed`.
- Gateway runs link the active prompt version when one exists. Newly registered systems receive a default active `v1` prompt version.

## V2 multi-agent governance model

The V2 direction is a genuine multi-agent governance system. Agents are bounded backend services with typed contracts, explicit permissions, observable decisions, and audit events. They should not silently change approval states or execute model/provider calls outside the gateway.

| Agent | Responsibilities |
|---|---|
| Retrieval Agent | Semantic retrieval, hybrid retrieval, reranking, source grounding. |
| Evaluation Agent | Hallucination scoring, groundedness, policy validation, confidence scoring. |
| Compliance Agent | PII detection, policy checks, prompt injection detection, output sanitisation. |
| Human Review Agent | Escalate risky outputs, route to reviewer, generate audit summary, maintain approval workflow. |
| Reporting Agent | Telemetry, cost tracking, latency metrics, weekly insights. |

## Dynamic risk scoring

Suggested MVP formula:

```text
base_score = risk_level_weight
+ personal_data_weight
+ input_pii_weight
+ prompt_injection_weight
+ sensitive_document_weight
+ unapproved_prompt_weight
+ user_permission_weight
```

Example weights:

| Factor | Weight |
|---|---:|
| Low risk system | 10 |
| Medium risk system | 30 |
| High risk system | 55 |
| Critical risk system | 80 |
| Contains personal data | +15 |
| PII detected in input | +15 |
| PII detected in output | +25 |
| Prompt injection signal | +35 |
| Sensitive retrieved document | +15 |
| Human oversight required | +10 |
| Unapproved/pending system | Block, not score |
| Blocked system | Block, not score |

Thresholds:

| Score | Route |
|---:|---|
| 0–34 | Allow. |
| 35–59 | Allow with review or review if flagged. |
| 60–79 | Hold for review. |
| 80+ | Block or critical review. |

These thresholds are demo defaults and should be configurable.

## Post-execution evaluation model

Checks:

| Check | What it detects | MVP implementation |
|---|---|---|
| Input PII | Synthetic personal data in user input. | Local regex detector. |
| Output PII | Sensitive data in generated output. | Local regex detector. |
| Output safety | Harmful/toxic/policy-violating text. | Heuristic/local provider. |
| Groundedness | Output unsupported by retrieved docs. | Source overlap heuristic. |
| Relevance | Output does not answer the request. | Keyword/embedding heuristic later. |
| Consistency | Contradiction or fabricated detail. | Heuristic/manual review. |
| Cost/latency anomaly | Unexpected usage. | Thresholds. |

Evaluation result should include:

- Overall score.
- Per-check scores.
- Flags.
- Explanation.
- Evidence snippets where safe.

### Episode 6 local evaluation rules

Episode 6 supports a provider progression for the Evaluation Agent. These evaluators are prototype signals only:

| Provider | Role |
|---|---|
| `LocalEvaluationProvider` | Fast token-overlap baseline. |
| `SemanticLocalEvaluationProvider` | Dependency-free semantic-ish local evaluator using stemming, synonym groups, phrase overlap, sentence-level support, and unsupported-number detection. |
| `OllamaEvaluationProvider` | Optional local model judge through Ollama. It asks for structured JSON and falls back to `SemanticLocalEvaluationProvider` if Ollama is unavailable. |

Dimensions:

- `relevance_score`: overlap or semantic-ish similarity between prompt/input terms and output terms.
- `groundedness_score`: source support against supplied retrieved documents. Runs without retrieved documents receive a conservative local grounding score.
- `hallucination_flag`: true when output contains explicit unsupported-claim signals or when retrieved context exists and grounding is very weak.
- `evaluation_score`: weighted score using relevance and groundedness.

Risk-adjusted default thresholds:

| Risk level | Threshold |
|---|---:|
| low | 55 |
| medium | 70 |
| high | 80 |
| critical | 90 |

If the score falls below the threshold or the hallucination flag is true, the model run is marked `requires_review`. These checks are governance heuristics, not proof of truth, safety, or compliance.

The V2 direction is to let multiple bounded evaluation agents contribute separate signals, for example a local semantic scorer, a local Ollama judge, a policy validator, and later Azure/OpenAI evaluators. The final route decision should aggregate those signals with explicit reasons rather than letting any evaluator silently change approval status.

### Episode 5 local PII rules

Episode 5 uses `HybridLocalPIIDetector`, a free local heuristic detector intended for synthetic demo data and obvious structured patterns only.

Detected patterns:

- Email addresses.
- Phone numbers.
- Labelled names, for example `Customer name: Alex Morgan`.
- Labelled account IDs, for example `Account ID: ACCT-12345`.
- Labelled addresses, for example `Address: 10 Demo Street`.
- Labelled dates of birth, postal codes, and national IDs.
- Spaced IBAN-like bank account values.
- Payment-card-like values that pass a Luhn checksum.

If input PII is detected, the run stores `input_pii_result`, creates a `pii_detected_input` incident, and routes the run to review when execution occurs. If output PII is detected, the run stores `output_pii_result`, creates a `pii_detected_output` incident, and routes the run to review.

Detector output uses redacted snippets such as `[REDACTED_EMAIL]`. The local detector also exposes a full-text redaction utility for future pre-LLM redaction. This is not comprehensive PII detection and must not be described as a compliance guarantee.
- Review requirement.

## Human review routing

Episode 7 implements local human review records. The review queue is not a policy label; it is an operational workflow where a reviewer inspects run evidence, risk flags, evaluation output, linked incidents, and retrieved documents before recording a decision.

Implemented local review creation rules:

- PII is detected in the input.
- PII is detected in the output.
- Evaluation score is below the configured threshold.
- Evaluation raises a hallucination flag.
- System risk level is `high` and `human_oversight_required` is true.

Planned future routing rules:

- Prompt injection detected.
- Critical risk system generates output.
- Reviewer is explicitly requested.

Review priorities:

| Priority | Trigger |
|---|---|
| Critical | Critical risk, blocked system attempt, severe PII exposure. |
| High | PII output, jailbreak, high-risk system. |
| Medium | Hallucination, medium risk with failed eval. |
| Low | Low relevance, minor formatting issues. |

Decision statuses:

| Status | Meaning |
|---|---|
| `pending` | Awaiting reviewer decision. |
| `approved` | Reviewer accepted the run evidence/output. |
| `rejected` | Reviewer rejected the run evidence/output. |
| `escalated` | Reviewer routed the case for higher-level handling. |

Reviewer decisions require reviewer ID, reviewer name, notes, and timestamp. Each decision records an audit event. Rejected and escalated runs remain marked `requires_review`.

## Incident creation policy

Create incident if:

- PII exposed in output for a medium/high/critical system.
- Prompt injection/jailbreak signal is high severity.
- System execution attempted while blocked.
- Output contains a policy violation.
- Hallucination is detected in a high-risk context.
- Cost/usage anomaly exceeds threshold.

Do not create an incident for every minor failed evaluation, or the dashboard becomes noisy. Use review queue for lower-severity items.

## Audit policy

Audit events are required for:

- System create/update.
- Approval status changes.
- Prompt version activation.
- Gateway route decisions.
- Review creation and decision.
- Incident creation/update/resolution.
- Audit export.
- Integration setting changes.

## Governance posture score

Optional MVP+ feature.

Suggested components:

| Component | Weight |
|---|---:|
| Registry completeness | 20 |
| Approval coverage | 20 |
| Review SLA | 15 |
| Incident resolution | 15 |
| Evaluation pass rate | 15 |
| Data-source classification coverage | 10 |
| Prompt version control | 5 |

Example:

```text
Governance posture: 72 / 100
```

Display explanation:

```text
This score is a governance signal based on registry completeness, unresolved incidents, review backlog, and evaluation failure rates. It is not a compliance certification.
```

## Framework alignment

### NIST AI RMF mapping

| NIST AI RMF function | Project feature |
|---|---|
| Govern | Registry, ownership, approvals, policies, audit logs. |
| Map | System purpose, data sources, departments, risk levels. |
| Measure | Evaluations, PII checks, groundedness, failure rates. |
| Manage | Review queue, incidents, blocking, remediation, exports. |

### Responsible AI principles mapping

| Principle | Project feature |
|---|---|
| Transparency | System detail pages, run logs, audit logs. |
| Accountability | Owners, reviewers, decisions, audit trail. |
| Privacy | PII detection, redaction, review routing. |
| Safety | Prompt and output checks. |
| Reliability | Evaluations and failure trends. |
| Human oversight | Review queue and decision workflow. |

## Governance language rules

Use:

- “Risk signal.”
- “Governance evidence.”
- “Approval workflow.”
- “Audit-ready export.”
- “Framework-aligned prototype.”

Avoid:

- “Fully compliant.”
- “Regulator approved.”
- “Guaranteed safe.”
- “Eliminates hallucinations.”
- “Automatic compliance.”

## Limitations to show clearly

- Risk scoring is configurable and contextual.
- PII detection is imperfect.
- Groundedness does not prove truth.
- Human review can still make mistakes.
- Audit logs are only useful if access and retention are managed.
- Governance dashboards can create false confidence if metrics are not interpreted carefully.
