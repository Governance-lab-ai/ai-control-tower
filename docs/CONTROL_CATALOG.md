# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-19  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


# Control Catalogue

## Purpose

This document defines the product controls that the AI Governance Control Tower should implement or simulate.

A control is a concrete mechanism that reduces risk, creates evidence, routes a decision, or improves accountability.

The catalogue uses this structure:

```text
Control ID
Name
Purpose
Risk addressed
Implementation
Evidence generated
Framework alignment
Limitations
Maturity
```

This catalogue should be treated as a living document. New controls should be added as the project grows.

## Control ID format

```text
ACT-<DOMAIN>-<NUMBER>
```

Domains:

| Domain | Meaning |
|---|---|
| `REG` | Registry and inventory |
| `APP` | Approval and lifecycle |
| `GW` | Governance gateway |
| `RISK` | Risk scoring and classification |
| `EVAL` | Evaluations and testing |
| `REV` | Human review |
| `INC` | Incidents and remediation |
| `AUD` | Audit and evidence |
| `SEC` | Security and privacy |
| `OBS` | Observability and telemetry |
| `POL` | Policy management |
| `INT` | Integrations |

## Control severity and maturity

| Field | Values |
|---|---|
| Risk criticality | Low, Medium, High, Critical |
| Maturity | MVP, Later, External |
| Enforcement mode | Inform, Warn, Hold, Block |

## Registry and inventory controls

### ACT-REG-001 — AI system registration

**Purpose:** Ensure AI systems are visible before or during use.

**Risk addressed:** Shadow AI, unowned systems, undocumented use cases, missing accountability.

**Implementation:** Require each governed AI system to be registered with name, description, department, owner, model/provider, intended users, data sources, personal data flag, human oversight flag, risk level, and approval status.

**Evidence generated:**

- `ai_system.created`
- `ai_system.updated`
- `audit_event`
- `system_export`

**Framework alignment:** NIST Govern/Map, ISO/IEC 42001 roles/lifecycle, EU AI Act documentation support.

**Limitations:** Does not detect unregistered AI systems unless discovery integrations are added.

**Maturity:** MVP

---

### ACT-REG-002 — Accountable owner assignment

**Purpose:** Ensure every AI system has a named accountable owner.

**Risk addressed:** Unclear accountability, orphaned systems, unresolved incidents.

**Implementation:** Registration requires an owner. Owner changes create audit events.

**Evidence generated:**

- `owner_assignment`
- `owner_changed`
- `audit_event`

**Framework alignment:** NIST Govern, ISO/IEC 42001 roles and responsibilities, OECD accountability.

**Limitations:** Tool assignment does not guarantee organisational accountability.

**Maturity:** MVP

---

### ACT-REG-003 — Data source declaration

**Purpose:** Make data dependencies and sensitivity visible.

**Risk addressed:** Unapproved data use, personal data leakage, sensitive data exposure, weak retrieval governance.

**Implementation:** Require AI systems to declare data sources and sensitivity levels. Later, integrate with Microsoft Purview or another catalogue.

**Evidence generated:**

- `data_source`
- `data_source_link`
- `sensitivity_label`
- `audit_event`

**Framework alignment:** NIST Map, ISO/IEC 42001 lifecycle/risk, EU AI Act documentation support.

**Limitations:** Data-source declarations may be incomplete without automated discovery.

**Maturity:** MVP/Later

---

## Approval and lifecycle controls

### ACT-APP-001 — Approval state gate

**Purpose:** Prevent unapproved systems from executing through the governance gateway.

**Risk addressed:** Unreviewed AI deployment, unauthorised model use, unmanaged risk.

**Implementation:** Gateway checks `approval_status`. `pending`, `blocked`, and `needs_changes` systems cannot execute unless explicitly configured for test mode.

**Evidence generated:**

- `route_decision=block`
- `blocked_model_run`
- `approval_status_checked`
- `audit_event`

**Framework alignment:** NIST Govern/Manage, ISO/IEC 42001 lifecycle controls, EU AI Act quality/risk management support.

**Limitations:** Does not prevent use outside the gateway.

**Maturity:** MVP

---

### ACT-APP-002 — Approval status audit trail

**Purpose:** Record changes in system approval state.

**Risk addressed:** Untraceable approvals, weak governance evidence, informal changes.

**Implementation:** Any approval transition creates an append-only audit event with actor, before state, after state, reason, timestamp, and optional review note.

**Evidence generated:**

- `approval_status_changed`
- `audit_event`

**Framework alignment:** NIST Govern, ISO/IEC 42001 lifecycle/audit evidence, OECD accountability.

**Limitations:** Depends on reliable identity and permissions.

**Maturity:** MVP

---

### ACT-APP-003 — Retired system lock

**Purpose:** Prevent retired systems from being used accidentally.

**Risk addressed:** Zombie AI systems, stale prompts, unsupported providers, unmonitored legacy systems.

**Implementation:** `retired` systems cannot execute through the gateway. Attempts are logged.

**Evidence generated:**

- `retired_system_execution_attempt`
- `route_decision=block`
- `audit_event`

**Framework alignment:** NIST Manage, ISO/IEC 42001 lifecycle management.

**Limitations:** Does not delete historical records.

**Maturity:** MVP

---

## Governance gateway controls

### ACT-GW-001 — Governed execution gateway

**Purpose:** Route model calls through a central governance decision point.

**Risk addressed:** Unlogged AI activity, missing checks, direct frontend/provider calls, inconsistent controls.

**Implementation:** AI apps call `POST /governance/run`. The backend performs approval, role, prompt, PII, risk, provider, evaluation, review, and audit steps.

**Evidence generated:**

- `model_run`
- `pre_check_result`
- `route_decision`
- `evaluation_result`
- `audit_event`

**Framework alignment:** NIST Govern/Measure/Manage, EU AI Act logging/documentation support, ISO/IEC 42001 operational control.

**Limitations:** Requires applications to use the gateway or network/API enforcement to require it.

**Maturity:** MVP

---

### ACT-GW-002 — Route decision explanation

**Purpose:** Make every gateway decision explainable.

**Risk addressed:** Black-box governance, arbitrary blocking, weak review evidence.

**Implementation:** Gateway returns and stores decision reasons, failed checks, risk score factors, and route metadata.

**Evidence generated:**

- `route_reasons`
- `risk_score_breakdown`
- `evaluation_flags`

**Framework alignment:** NIST transparency/accountability, OECD transparency, ISO/IEC 42001 traceability support.

**Limitations:** Explanations may reflect heuristic checks, not full model reasoning.

**Maturity:** MVP

---

### ACT-GW-003 — Hold before execution

**Purpose:** Stop high-risk requests before model output is generated.

**Risk addressed:** Irreversible disclosure, unsafe action generation, high-risk automation without review.

**Implementation:** If pre-execution score or policy requires it, create a human review item and return `202 held_for_review`.

**Evidence generated:**

- `human_review.created`
- `route_decision=hold_for_review`
- `pre_check_result`
- `audit_event`

**Framework alignment:** NIST Manage, EU AI Act human oversight support, ISO/IEC 42001 risk treatment.

**Limitations:** Requires a functional reviewer workflow and SLA.

**Maturity:** MVP

---

### ACT-GW-004 — Block on critical policy violation

**Purpose:** Prevent execution when use is outside allowed policy.

**Risk addressed:** Critical misuse, prohibited use, blocked systems, unapproved high-impact automation.

**Implementation:** Route as `block` when an input, system state, role, prompt version, or risk score exceeds blocking rules.

**Evidence generated:**

- `blocked_model_run`
- `incident` optional
- `audit_event`

**Framework alignment:** NIST Manage, ISO/IEC 42001 controls, OWASP risk handling.

**Limitations:** Requires accurate policy rules and careful tuning to avoid overblocking.

**Maturity:** MVP

---

## Risk controls

### ACT-RISK-001 — Configurable risk scoring

**Purpose:** Generate a transparent risk signal for routing.

**Risk addressed:** Inconsistent judgement, invisible risk accumulation, weak prioritisation.

**Implementation:** Calculate score using risk level, personal data, PII flags, prompt-injection signal, sensitive documents, human oversight requirement, prompt status, and user permissions.

**Evidence generated:**

- `risk_score`
- `risk_score_breakdown`
- `route_decision`

**Framework alignment:** NIST Measure/Manage, ISO/IEC 42001 risk management.

**Limitations:** Risk scores are decision-support signals, not objective truth.

**Maturity:** MVP

---

### ACT-RISK-002 — Critical risk block by default

**Purpose:** Prevent the MVP from normalising unsafe high-impact automation.

**Risk addressed:** Overconfident demos, safety-critical use without controls, false assurance.

**Implementation:** `critical` risk systems are blocked by default unless explicitly configured for non-production simulation mode.

**Evidence generated:**

- `critical_risk_block`
- `audit_event`
- `incident` optional

**Framework alignment:** NIST Manage, ISO/IEC 42001 risk treatment.

**Limitations:** Real organisations need formal risk-acceptance processes.

**Maturity:** MVP

---

### ACT-RISK-003 — Personal data risk uplift

**Purpose:** Increase scrutiny when personal or sensitive data is involved.

**Risk addressed:** Privacy leakage, inappropriate processing, poor retention decisions.

**Implementation:** Add configurable score weight and review threshold when system or input contains personal data. Use Microsoft Presidio/Presidio where available, with regex, NER, and entity detection fallback for local/demo mode.

**Evidence generated:**

- `personal_data_flag`
- `pii_check_result`
- `risk_score_breakdown`

**Framework alignment:** NIST Map/Measure, OECD human rights/fairness, EU documentation/logging support.

**Limitations:** MVP PII detection is heuristic and may miss sensitive context.

**Maturity:** MVP

---

## Evaluation controls

### ACT-EVAL-001 — Input PII check

**Purpose:** Detect personal data in prompts before model execution.

**Risk addressed:** Sensitive data exposure, privacy violations, unapproved processing.

**Implementation:** Use Microsoft Presidio/Presidio where available. Local/demo mode may fall back to regex, NER, and entity detection for names, emails, phone numbers, account numbers, addresses, and payment-card-like values.

**Evidence generated:**

- `input_pii_flag`
- `evaluation_result`
- `route_decision`

**Framework alignment:** NIST Measure, ISO/IEC 42001 risk control, OWASP sensitive information disclosure.

**Limitations:** False positives and false negatives are expected.

**Maturity:** MVP

---

### ACT-EVAL-002 — Prompt injection check

**Purpose:** Detect prompt-injection and jailbreak attempts.

**Risk addressed:** System prompt leakage, tool misuse, policy bypass, retrieval compromise.

**Implementation:** Pattern-based MVP checks for jailbreak attempts, suspicious prompt heuristics, hidden-instruction requests, policy-bypass requests, and unapproved tool instructions. Later integrate Prompt Shields, Garak, Promptfoo, or other security test providers.

**Evidence generated:**

- `prompt_injection_flag`
- `security_flag`
- `route_decision`
- `incident` optional

**Framework alignment:** OWASP LLM Top 10, NIST security/resilience, ISO/IEC 42001 operational controls.

**Limitations:** Simple pattern checks cannot catch sophisticated attacks.

**Maturity:** MVP/Later

---

### ACT-EVAL-006 — Pre-LLM redaction

**Purpose:** Reduce sensitive data sent to model providers.

**Risk addressed:** Unnecessary disclosure of personal data, unsafe provider context, excessive collection.

**Implementation:** Redact names, emails, phone numbers, and account numbers before provider execution when system policy requires redaction. Preserve redaction metadata so reviewers can understand what categories were removed without exposing raw values.

**Evidence generated:**

- `redaction_event`
- `redacted_entity_types`
- `route_decision`

**Framework alignment:** Privacy, data minimisation, OWASP sensitive information disclosure.

**Limitations:** Redaction quality depends on detector quality and may require human review for high-risk systems.

**Maturity:** MVP/Later

---

### ACT-EVAL-003 — Output PII check

**Purpose:** Detect sensitive data in generated output before release or review.

**Risk addressed:** Disclosure of personal data, accidental leakage from retrieval context.

**Implementation:** Run PII detection on output. Depending on severity, allow with review, hold, or block.

**Evidence generated:**

- `output_pii_flag`
- `evaluation_result`
- `human_review` optional
- `incident` optional

**Framework alignment:** NIST Measure/Manage, OWASP sensitive information disclosure.

**Limitations:** Does not prove data protection compliance.

**Maturity:** MVP

---

### ACT-EVAL-004 — Groundedness check

**Purpose:** Estimate whether an output is supported by provided sources.

**Risk addressed:** Hallucination, unsupported claims, misleading summaries.

**Implementation:** Use source overlap heuristic in MVP; later integrate groundedness evaluators.

**Evidence generated:**

- `groundedness_score`
- `source_overlap`
- `evaluation_result`
- `review_required`

**Framework alignment:** NIST Measure, OECD transparency/robustness.

**Limitations:** Source overlap is weak and can miss semantic errors.

**Maturity:** MVP/Later

---

### ACT-EVAL-005 — Evaluation result record

**Purpose:** Store check results in a consistent, reviewable format.

**Risk addressed:** Lost test results, inconsistent review data, weak audit evidence.

**Implementation:** Every run gets an `evaluation_result` with per-check status, severity, score, flags, explanations, and safe evidence snippets.

**Evidence generated:**

- `evaluation_result`
- `evaluation_check`
- `audit_event`

**Framework alignment:** NIST Measure, ISO/IEC 42001 monitoring, EU logging/documentation support.

**Limitations:** Evidence must be redacted and access-controlled.

**Maturity:** MVP

---

## Human review controls

### ACT-REV-001 — Human review routing

**Purpose:** Route risky, uncertain, or policy-sensitive outputs to accountable reviewers.

**Risk addressed:** Overreliance on automation, uncontrolled high-risk outputs, missing escalation.

**Implementation:** Create review items when route decision, risk score, or evaluation flags require review.

**Evidence generated:**

- `human_review.created`
- `review_reason`
- `review_sla`
- `audit_event`

**Framework alignment:** EU human oversight support, NIST Manage, OECD accountability.

**Limitations:** Reviewers need training, time, and authority.

**Maturity:** MVP

---

### ACT-REV-002 — Review decision audit

**Purpose:** Record approve, reject, escalate, or request-changes decisions.

**Risk addressed:** Untraceable human intervention, inconsistent remediation.

**Implementation:** Review action endpoint records actor, action, reason, timestamp, and outcome.

**Evidence generated:**

- `review_decision`
- `audit_event`
- `incident` optional

**Framework alignment:** NIST Govern/Manage, ISO/IEC 42001 accountability.

**Limitations:** Does not guarantee decision quality.

**Maturity:** MVP

---

### ACT-REV-003 — Reviewer evidence display

**Purpose:** Give reviewers enough context to make decisions.

**Risk addressed:** Rubber-stamp review, incomplete context, poor escalation.

**Implementation:** Review detail page shows input/output, flags, risk score, route reasons, system owner, data source, and safe evidence snippets.

**Evidence generated:**

- `review_viewed` optional
- `review_decision`

**Framework alignment:** Human oversight, accountability, transparency.

**Limitations:** Must avoid overexposing sensitive content.

**Maturity:** MVP/Later

---

## Incident controls

### ACT-INC-001 — Incident creation

**Purpose:** Escalate serious governance failures into incident records.

**Risk addressed:** Repeated failures, untracked harm, unresolved policy violations.

**Implementation:** Create incident for PII exposure, jailbreak/policy violation, hallucination in high-risk context, blocked critical use, or reviewer escalation.

**Evidence generated:**

- `incident.created`
- `incident_category`
- `severity`
- `linked_model_run`
- `audit_event`

**Framework alignment:** NIST Manage, ISO/IEC 42001 improvement, EU corrective action support.

**Limitations:** Incident thresholds require tuning.

**Maturity:** MVP

---

### ACT-INC-002 — Incident lifecycle

**Purpose:** Track investigation, remediation, resolution, or dismissal.

**Risk addressed:** Open-ended incidents, weak corrective action, no learning loop.

**Implementation:** Incidents move through `open`, `investigating`, `resolved`, `dismissed`, with notes, owner, severity, and resolution reason.

**Evidence generated:**

- `incident_status_changed`
- `remediation_note`
- `audit_event`

**Framework alignment:** NIST Manage, ISO/IEC 42001 continual improvement.

**Limitations:** Remediation effectiveness must be assessed separately.

**Maturity:** MVP

---

### ACT-INC-003 — System block after severe incident

**Purpose:** Stop continued use after serious unresolved incidents.

**Risk addressed:** Known-bad system continues operating, repeated harm.

**Implementation:** Severe incident can trigger `approval_status=blocked` or `needs_changes`.

**Evidence generated:**

- `approval_status_changed`
- `incident_link`
- `audit_event`

**Framework alignment:** NIST Manage, ISO/IEC 42001 risk treatment.

**Limitations:** Requires governance authority to block systems.

**Maturity:** Later

---

## Audit and evidence controls

### ACT-AUD-001 — Append-only audit event

**Purpose:** Preserve a reliable history of governance actions.

**Risk addressed:** Tampering, missing accountability, unverifiable claims.

**Implementation:** Record actor, action, entity type, entity ID, before state, after state, timestamp, and metadata. Normal app flows cannot update/delete audit events.

**Evidence generated:**

- `audit_event`

**Framework alignment:** NIST accountability, ISO/IEC 42001 records, EU logging/documentation support.

**Limitations:** Full immutability requires database/storage hardening.

**Maturity:** MVP

---

### ACT-AUD-002 — Evidence item linking

**Purpose:** Link evidence to controls, runs, reviews, incidents, and exports.

**Risk addressed:** Scattered evidence, audit friction, unverifiable control operation.

**Implementation:** Create `evidence_item` records that point to model runs, evaluations, reviews, incidents, exports, and control tests.

**Evidence generated:**

- `evidence_item`
- `control_evidence_link`

**Framework alignment:** NIST Govern/Measure/Manage, ISO/IEC 42001 records, EU documentation support.

**Limitations:** Requires careful access controls and retention.

**Maturity:** Later

---

### ACT-AUD-003 — Audit export

**Purpose:** Produce filtered evidence for internal review, demo, or assurance.

**Risk addressed:** Manual evidence gathering, inconsistent reports, weak stakeholder communication.

**Implementation:** Export CSV/JSON evidence by system, date range, incident, control, or framework mapping.

**Evidence generated:**

- `audit_export`
- `evidence_pack`

**Framework alignment:** Audit readiness, transparency, accountability.

**Limitations:** Export does not equal external certification.

**Maturity:** MVP/Later

---

## Security and privacy controls

### ACT-SEC-001 — No secrets in frontend

**Purpose:** Prevent model/API credentials from being exposed in the browser.

**Risk addressed:** Credential leakage, unauthorised provider access.

**Implementation:** Frontend calls backend only. Backend uses provider adapters and secret manager.

**Evidence generated:**

- Code review/test evidence
- Integration configuration

**Framework alignment:** Secure design, OWASP, NIST security/resilience.

**Limitations:** Requires CI checks and operational secret management.

**Maturity:** MVP

---

### ACT-SEC-002 — Prompt/output logging minimisation

**Purpose:** Reduce sensitive data exposure in logs.

**Risk addressed:** Privacy leakage through telemetry, overcollection, unsafe audit exports.

**Implementation:** Do not log full prompts/outputs to console by default. Store prompts, outputs, retrieved documents, approvals, costs, and reviewer actions in secured evidence records with redaction and access control.

**Evidence generated:**

- `redaction_event`
- `model_run_content_policy`
- `audit_event`

**Framework alignment:** Privacy, security, proportionality.

**Limitations:** Retention policy and encryption are required for production.

**Maturity:** MVP/Later

---

### ACT-SEC-003 — Role-based access control

**Purpose:** Restrict governance actions to authorised users.

**Risk addressed:** Unauthorised approvals, inappropriate access to sensitive runs, weak segregation of duties.

**Implementation:** Local mock RBAC in MVP with `admin`, `analyst`, `reviewer`, and `auditor` roles; Entra ID / SSO later.

**Evidence generated:**

- `permission_check`
- `access_denied_event`
- `audit_event`

**Framework alignment:** NIST Govern, ISO/IEC 42001 roles, security best practice.

**Limitations:** Local mock users are not production identity.

**Maturity:** MVP/Later

---

## Observability controls

### ACT-OBS-001 — Model run telemetry

**Purpose:** Capture operational data about governed AI usage.

**Risk addressed:** No visibility into usage, cost, latency, failures, or evaluation rates.

**Implementation:** Store provider, model version, input/output token count, latency, cost estimate, route decision, and eval summary.

**Evidence generated:**

- `model_run`
- `usage_metric`
- `cost_metric`
- `latency_metric`

**Framework alignment:** NIST Measure/Manage, ISO/IEC 42001 monitoring.

**Limitations:** Not a replacement for full observability platforms.

**Maturity:** MVP

---

### ACT-OBS-002 — OpenTelemetry-compatible extension

**Purpose:** Allow governance telemetry to connect to existing engineering observability.

**Risk addressed:** Governance dashboard isolated from production operations.

**Implementation:** Add telemetry provider interface and later emit traces/events compatible with OpenTelemetry and Azure Monitor/Application Insights.

**Evidence generated:**

- `trace_id`
- `span_id`
- `telemetry_event`

**Framework alignment:** Operational monitoring and auditability.

**Limitations:** Later-stage integration.

**Maturity:** Later

---

## Policy controls

### ACT-POL-001 — Policy version record

**Purpose:** Track which policy rules were active when a decision occurred.

**Risk addressed:** Unknown rule state, impossible historical reconstruction.

**Implementation:** Store policy version ID on route decisions and evaluations.

**Evidence generated:**

- `policy_version`
- `policy_version_used`
- `audit_event`

**Framework alignment:** NIST Govern/Manage, ISO/IEC 42001 control management.

**Limitations:** Requires formal policy management process.

**Maturity:** Later

---

### ACT-POL-002 — Policy-as-code decision interface

**Purpose:** Allow executable policies to be separated from application logic.

**Risk addressed:** Hard-coded rules, poor reviewability, inconsistent enforcement.

**Implementation:** Define `PolicyDecisionProvider`; start with Python rules, later support OPA/Rego or another policy engine.

**Evidence generated:**

- `policy_decision`
- `policy_input`
- `policy_version`

**Framework alignment:** Governance as executable control.

**Limitations:** Policy-as-code must be governed like software.

**Maturity:** Later

---

## Integration controls

### ACT-INT-001 — Provider adapter boundary

**Purpose:** Prevent vendor lock-in and keep governance logic separate from provider code.

**Risk addressed:** Hard-coded providers, untestable integrations, cloud migration risk.

**Implementation:** Use interfaces for LLM, safety, groundedness, secrets, telemetry, identity, and data governance providers.

**Evidence generated:**

- Integration status
- Provider configuration metadata

**Framework alignment:** Lifecycle, security, operational resilience.

**Limitations:** Adapters still need real-world testing.

**Maturity:** MVP

---

### ACT-INT-002 — External evaluator plugin

**Purpose:** Allow specialised evaluation tools to feed governance decisions.

**Risk addressed:** Weak local heuristics, duplicated eval tooling, poor testing depth.

**Implementation:** Add evaluator provider interface for Inspect, Dioptra, Promptfoo, Giskard, Garak, Ragas, or custom evals.

**Evidence generated:**

- `external_evaluation_result`
- `evaluator_provider`
- `test_report`

**Framework alignment:** NIST Measure, ISO/IEC 42001 monitoring, assurance.

**Limitations:** External eval results need interpretation and context.

**Maturity:** Later

## MVP minimum control set

For the first working demo, prioritise:

1. ACT-REG-001 — AI system registration
2. ACT-REG-002 — Accountable owner assignment
3. ACT-APP-001 — Approval state gate
4. ACT-GW-001 — Governed execution gateway
5. ACT-GW-002 — Route decision explanation
6. ACT-RISK-001 — Configurable risk scoring
7. ACT-EVAL-001 — Input PII check
8. ACT-EVAL-002 — Prompt injection check
9. ACT-EVAL-003 — Output PII check
10. ACT-EVAL-006 — Pre-LLM redaction
11. ACT-EVAL-005 — Evaluation result record
12. ACT-REV-001 — Human review routing
13. ACT-REV-002 — Review decision audit
14. ACT-INC-001 — Incident creation
15. ACT-AUD-001 — Append-only audit event
16. ACT-SEC-001 — No secrets in frontend
17. ACT-OBS-001 — Model run telemetry
18. ACT-INT-001 — Provider adapter boundary

## Public wording guidance

Use:

> The Control Tower shows what governance controls look like when expressed as software decisions and evidence.

Avoid:

> The Control Tower proves an AI system is safe or compliant.
