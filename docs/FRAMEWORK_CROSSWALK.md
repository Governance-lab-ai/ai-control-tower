# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-19  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


# Framework Crosswalk

## Purpose

This document maps major AI governance frameworks and regulatory concepts to the Control Tower's concrete product controls and evidence objects.

This is not a legal interpretation and does not claim compliance. It is a practical engineering crosswalk:

```text
Framework concept
  -> product control
  -> evidence generated
  -> system component
  -> limitation
```

The crosswalk should help engineers, reviewers, and stakeholders understand how abstract governance language becomes operational evidence.

## Scope

Covered in this document:

- NIST AI Risk Management Framework
- EU AI Act concepts, especially high-risk AI system obligations
- ISO/IEC 42001 AI management system concepts
- OECD AI Principles
- OWASP Top 10 for LLM Applications

Not covered yet:

- Sector-specific laws.
- Procurement rules.
- Local employment, health, finance, or consumer-protection law.
- Formal certification requirements.
- Organisation-specific policy packs.

## Crosswalk maturity labels

| Label | Meaning |
|---|---|
| `MVP` | Should be implemented in the first working version |
| `Later` | Useful after the MVP proves the core flow |
| `External` | Best handled by external tools or professional processes |
| `Not claimed` | The Control Tower can support evidence, but cannot make the claim itself |

## NIST AI RMF crosswalk

The NIST AI RMF Core is structured around Govern, Map, Measure, and Manage. The Control Tower should make those ideas operational without treating them as a checklist.

| NIST AI RMF function | Practical meaning | Control Tower support | Evidence generated | Maturity | Limitation |
|---|---|---|---|---|---|
| Govern | Establish accountability, policies, roles, oversight, risk culture | AI system registry, owner assignment, approval workflow, role-based review, audit events | `ai_system`, `approval_event`, `audit_event`, `policy_version` | MVP | Does not establish organisation-wide governance culture by itself |
| Map | Understand context, purpose, stakeholders, data, deployment environment | Registration fields for intended purpose, department, data sources, personal data, users, risk level | `ai_system`, `data_source`, `risk_assessment` | MVP/Later | Stakeholder and context analysis still needs human judgment |
| Measure | Assess risks, performance, failures, uncertainty, safety, fairness, robustness | Pre-execution checks, post-execution evaluations, PII flags, groundedness/relevance checks, eval integrations | `evaluation_result`, `model_run`, `risk_score`, `flag` | MVP/Later | MVP heuristics are not robust enough for high-stakes assurance |
| Manage | Prioritise, respond, route, mitigate, monitor, and improve | Route decisions, human review queue, incident management, remediation notes, dashboards | `human_review`, `incident`, `route_decision`, `remediation_event` | MVP | Does not guarantee risk mitigation was effective without organisational follow-through |

## EU AI Act concept crosswalk

The Control Tower should not claim EU AI Act compliance. It can, however, demonstrate operational mechanisms that may support documentation, logging, oversight, risk management, and evidence generation.

| EU AI Act concept | Practical engineering question | Control Tower support | Evidence generated | Maturity | Limitation |
|---|---|---|---|---|---|
| Risk classification | Is this system low, medium, high, or critical risk? | Risk-level field, critical-use block defaults, use-case metadata | `risk_level`, `risk_assessment`, `classification_reason` | MVP | Legal classification requires expert analysis and jurisdiction-specific review |
| Quality/risk management | Are risks identified, controlled, monitored, and reviewed? | Control catalogue, risk scoring, incidents, remediation workflow | `control_record`, `incident`, `review_decision` | Later | Does not replace a quality management system |
| Technical documentation | Can the organisation explain the system, purpose, data, controls, and lifecycle? | AI registry, prompt versions, data source metadata, system detail exports | `ai_system_export`, `prompt_version`, `data_source` | MVP/Later | Documentation must be validated and maintained by accountable owners |
| Logging | Are relevant AI operations captured for later review? | Model run log, evaluation log, route decision, audit event | `model_run`, `evaluation_result`, `audit_event` | MVP | Logging must handle privacy, retention, access control, and proportionality |
| Human oversight | When and how do people intervene? | Human review queue, hold-for-review route, escalation actions | `human_review`, `review_decision`, `review_sla` | MVP | Human review quality depends on training, authority, and incentives |
| Accuracy, robustness, cybersecurity | How are failure modes tested and monitored? | Evaluation layer, security checks, OWASP-aligned prompt injection controls | `evaluation_result`, `security_flag`, `test_report` | Later | MVP checks are basic and not enough for regulated systems |
| Corrective action | What happens after an issue is found? | Incident lifecycle, remediation notes, blocked status, system re-approval | `incident`, `remediation_event`, `approval_status_change` | MVP/Later | Organisational response is outside the tool unless enforced |
| Registration / declarations | Can evidence be exported for external governance processes? | Audit exports, system exports, evidence packs | `evidence_pack`, `audit_export` | Later | Does not complete external registration or declarations |

## ISO/IEC 42001 concept crosswalk

ISO/IEC 42001 is an AI management system standard. The Control Tower can support evidence and workflow for an AI management system, but it is not itself an ISO management system.

| ISO/IEC 42001 concept | Practical engineering question | Control Tower support | Evidence generated | Maturity | Limitation |
|---|---|---|---|---|---|
| AI management system | Is there a repeatable system for governing AI? | Registry, controls, approval workflows, incidents, audit events | `control_catalog`, `audit_event`, `dashboard_metric` | Later | Certification requires organisation-level scope, process, audit, and continual improvement |
| Roles and responsibilities | Who owns the AI system and who reviews risk? | Owner, department, reviewer role, governance admin | `owner_assignment`, `reviewer_assignment` | MVP | Tool cannot ensure real accountability without policy and leadership |
| Risk management | How are AI risks identified, assessed, treated, and reviewed? | Risk scoring, control catalogue, incident lifecycle | `risk_assessment`, `route_decision`, `incident` | MVP/Later | Requires human risk acceptance and periodic review |
| Impact assessment | Who may be affected and how? | Stakeholder and impact fields in system registration | `impact_assessment` | Later | Needs domain-specific analysis |
| Lifecycle management | What changed over time? | Prompt versions, approval status history, audit events, run history | `prompt_version`, `approval_event`, `audit_event` | MVP | Model/provider lifecycle changes need deeper integration |
| Supplier / provider oversight | Which providers and external tools are used? | Provider metadata, integration status, vendor notes | `provider_record`, `integration_status` | Later | Vendor risk management requires contracts and external due diligence |
| Monitoring and improvement | Are issues tracked and used to improve controls? | Incident trends, review outcomes, evaluation failure rates | `incident_trend`, `control_change`, `remediation_event` | MVP/Later | Tool reports signals; management must act on them |

## OECD AI Principles crosswalk

| OECD principle area | Control Tower support | Evidence generated | Limitation |
|---|---|---|---|
| Inclusive growth and well-being | Impact fields, stakeholder notes, incident tracking | `impact_assessment`, `incident` | Value alignment requires human and organisational judgment |
| Human rights, democratic values, fairness | Risk classification, human review, fairness integrations later | `human_review`, `fairness_report` | MVP does not prove rights protection or fairness |
| Transparency and explainability | Model run metadata, route reasons, evaluation explanations | `route_decision`, `evaluation_result`, `system_export` | Explanations may be incomplete or heuristic |
| Robustness, security, safety | Safety checks, prompt injection checks, security flags | `security_flag`, `test_report` | Requires ongoing adversarial testing |
| Accountability | Ownership, audit logs, review decisions, incidents | `owner_assignment`, `audit_event`, `review_decision` | Accountability is organisational, not only technical |

## OWASP LLM Top 10 crosswalk

| OWASP risk area | Control Tower support | Maturity |
|---|---|---|
| Prompt injection | Input checks, prompt injection flags, route blocking/holding | MVP |
| Sensitive information disclosure | PII checks, redaction, restricted logging | MVP |
| Supply chain / dependency risk | Provider inventory and integration metadata | Later |
| Data and system prompt leakage | Output checks, restricted exports, audit access control | Later |
| Insecure output handling | Route decisions, human review for risky outputs | MVP |
| Excessive agency | Agent/tool-call metadata and approval gates | Later |
| Overreliance | Human review, warnings, confidence/evidence display | MVP/Later |
| Model denial of service | Cost/latency anomaly detection | Later |
| Insecure plugin/tool design | Tool registry and permission gates | Later |
| Unbounded consumption | Cost/usage thresholds | MVP/Later |

## Evidence chain example

For a governed model run, the evidence chain should be:

```text
AI system
  -> approval status
  -> prompt version
  -> model run
  -> pre-check results
  -> route decision
  -> output
  -> post-check results
  -> review or incident
  -> audit event
  -> exportable evidence pack
```

## Required additions to the data model

To support this crosswalk cleanly, consider adding:

| Object | Purpose |
|---|---|
| `framework_reference` | Stores NIST/EU/ISO/OECD/OWASP references by ID |
| `control` | Stores implemented controls and owners |
| `control_framework_mapping` | Maps controls to framework concepts |
| `evidence_item` | Links evidence to controls, runs, reviews, incidents, and exports |
| `evidence_pack` | Groups evidence for a system, incident, or review period |
| `risk_assessment` | Stores human-entered and system-generated risk assessment data |
| `policy_version` | Stores executable or documented policy versions |
| `control_test_result` | Records whether a control test passed, failed, or needs review |

## Public wording guidance

Use this wording externally:

> The Control Tower does not claim compliance. It demonstrates how governance expectations can be translated into operational controls and evidence.

Avoid this wording:

> This makes organisations compliant with the EU AI Act, NIST, or ISO.

## References

- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI RMF Core: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
- EU AI Act service desk: https://ai-act-service-desk.ec.europa.eu/en/ai-act/
- EU AI Act Article 16: https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-16
- ISO/IEC 42001: https://www.iso.org/standard/42001
- ISO/IEC 42001 explanation: https://www.iso.org/home/insights-news/resources/iso-42001-explained-what-it-is.html
- OECD AI Principles: https://oecd.ai/en/ai-principles
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
