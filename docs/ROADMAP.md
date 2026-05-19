# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-12  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


## Roadmap strategy

Build credibility in layers:

1. **Local prototype that works.**
2. **Governance workflow that is clear.**
3. **Dashboard that looks distinct and serious.**
4. **Evaluation and review flow that proves the control concept.**
5. **Azure integration examples and selected real adapters.**
6. **Security and reliability hardening.**

Do not attempt full enterprise cloud deployment before the local system demonstrates value.

## Phase 0 — Product and repo foundation

**Goal:** align scope and create a clean starting point.

Estimated duration: 2–4 days.

Deliverables:

- Repository structure.
- Handover docs added to repo.
- Backend and frontend app shells.
- Docker Compose for Postgres.
- `.env.example` files.
- Initial GitHub Actions.
- Seed data plan.

Acceptance criteria:

- Repo can be cloned and both apps can start.
- Docs are visible and referenced from README.
- No cloud dependencies are required.

## Phase 1 — Core registry and data model

**Goal:** create the governance control plane.

Estimated duration: 1 week.

Deliverables:

- Database schema for companies, users, systems, data sources, prompt versions, audit events.
- AI system CRUD endpoints.
- Approval status update endpoint.
- Basic dashboard summary endpoint.
- System registry page.
- System detail page skeleton.

Acceptance criteria:

- User can register `Customer Support Summariser`.
- User can assign owner, department, model, data sources, risk, personal data flag, and human oversight flag.
- Approval changes create audit events.
- Registry table filters by department, risk, and status.

## Phase 2 — Governance gateway and model run logging

**Goal:** ensure AI execution flows through governance controls.

Estimated duration: 1–2 weeks.

Deliverables:

- `POST /governance/run`.
- Mock LLM provider.
- Model run table.
- Retrieved document table.
- Cost and latency capture.
- Prompt version linkage.
- Pre-execution checks for approval status and prompt policy.
- Pre-LLM redaction layer for names, emails, phone numbers, and account numbers.
- Run detail view.

Acceptance criteria:

- Approved system can execute a mock model run.
- Pending/blocked system cannot execute.
- Every execution attempt is logged.
- Every execution attempt creates an audit event.

## Phase 3 — Evaluation layer and risk routing

**Goal:** turn logs into actionable governance signals.

Estimated duration: 1–2 weeks.

Deliverables:

- PII detector using Microsoft Presidio/Presidio where available, with regex, NER, and entity detection fallback.
- Prompt injection/policy detector with jailbreak detection, suspicious prompt heuristics, and tool restriction logic.
- Redaction pipeline before provider calls for names, emails, phone numbers, and account numbers.
- Output safety heuristic.
- Groundedness/retrieval overlap heuristic.
- Evaluation score model.
- Review routing rules.
- Failed evaluations page.

Acceptance criteria:

- PII in input/output is detected and flagged.
- Sensitive values are redacted before LLM execution where configured.
- Jailbreak attempts and suspicious tool-use instructions are detected and routed.
- Risky outputs route to review.
- Failed evaluations are visible in dashboard.
- Evaluation scores are explained, not just shown.

## Phase 4 — Human review and incident workflow

**Goal:** prove human oversight and accountability.

Estimated duration: 1–2 weeks.

Deliverables:

- Human review queue page.
- Review detail page/drawer.
- Approve/reject/escalate actions.
- Incident creation rules.
- Incident list and detail page.
- Review and incident audit events.

Acceptance criteria:

- Reviewer can inspect run context, output, retrieved docs, flags, and scores.
- Reviewer can approve, reject, escalate, or request changes.
- Incidents can be opened and resolved.
- Review decisions are reflected in system/run history.

## Phase 5 — Command-centre dashboard design

**Goal:** make the product visually distinctive and story-ready.

Estimated duration: 1–2 weeks, can overlap with phases 2–4.

Deliverables:

- Design tokens implemented.
- Dark command-centre layout.
- Overview dashboard.
- Risk heatmap.
- Posture score.
- Recent incidents panel.
- Cost and usage panels.
- Audit table styling.

Acceptance criteria:

- Dashboard no longer looks like generic SaaS.
- Risk and review states are visually prominent.
- The dashboard works well for screenshots and video demos.
- Accessibility basics are checked.

## Phase 6 — Azure-aware adapters and documentation

**Goal:** show enterprise integration maturity without making Azure a blocker.

Estimated duration: 1–2 weeks.

Deliverables:

- Azure OpenAI adapter stub or working implementation.
- Azure AI Content Safety adapter stub or working implementation.
- Azure Key Vault secret manager stub or working implementation.
- Application Insights telemetry adapter stub.
- Integration settings page.
- `AZURE_INTEGRATION.md` complete.

Acceptance criteria:

- Local app can run without Azure.
- Code clearly shows where Azure services plug in.
- Integration cards show Local/Configured/Connected states.
- At least one Azure adapter can be enabled with environment variables if credentials are available.

## Phase 7 — Testing, hardening, and demo polish

**Goal:** make the project credible for public release.

Estimated duration: 1 week.

Deliverables:

- Unit tests for risk engine and routing.
- Backend integration tests.
- Frontend component tests.
- Playwright smoke test.
- Security checklist pass.
- Demo seed data.
- Demo script.
- README recording instructions.

Acceptance criteria:

- CI passes.
- Demo can be reset with one command.
- No secrets or real personal data in repo.
- Critical flows work reliably.

## Phase 8 — Optional production-oriented extension

**Goal:** show production architecture awareness.

Estimated duration: open-ended.

Possible deliverables:

- Azure Container Apps deployment.
- Azure Database for PostgreSQL.
- Microsoft Entra ID auth.
- Key Vault secrets.
- Application Insights traces.
- Microsoft Purview metadata import.
- Async evaluation queue.
- Retention policies.
- Multi-tenant isolation.
- Terraform/Bicep infrastructure.

## V2 — Multi-agent governance system

**Goal:** evolve the Control Tower from a gateway-led MVP into a genuine multi-agent governance system with bounded, auditable agents.

This is a V2 direction, not a requirement for the local MVP. Each agent must have typed inputs and outputs, backend execution only, explicit permissions, and audit events.

### Agent 1 — Retrieval Agent

Responsibilities:

- Semantic retrieval.
- Hybrid retrieval.
- Reranking.
- Source grounding.

### Agent 2 — Evaluation Agent

Responsibilities:

- Hallucination scoring.
- Groundedness.
- Policy validation.
- Confidence scoring.

### Agent 3 — Compliance Agent

Responsibilities:

- PII detection.
- Policy checks.
- Prompt injection detection.
- Output sanitisation.

### Agent 4 — Human Review Agent

Responsibilities:

- Escalate risky outputs.
- Route to reviewer.
- Generate audit summary.
- Maintain approval workflow.

### Agent 5 — Reporting Agent

Responsibilities:

- Telemetry.
- Cost tracking.
- Latency metrics.
- Weekly insights.

## MVP scope boundary

Include in MVP:

- Registry.
- System detail.
- Governance gateway.
- Mock model run.
- Run logging.
- Basic checks.
- Human review queue.
- Incidents.
- Audit logs.
- Overview dashboard.
- Azure integration docs/stubs.

Exclude from MVP:

- Production-grade multi-tenancy.
- Legal compliance certification.
- Full Purview integration.
- Full SIEM integration.
- Complex custom workflow builder.
- Real-time streaming telemetry.
- Automated remediation without human approval.

## Backlog by priority

### P0 — Must have

- System registry.
- Approval status gate.
- Governance gateway.
- Model run log.
- PII detection using Presidio/Microsoft Presidio where possible, plus regex, NER, and entity detection fallback.
- Prompt injection detection including jailbreak detection, suspicious prompt heuristics, and tool restriction logic.
- Redaction layer before LLM calls for names, emails, phone numbers, and account numbers.
- Role-based access levels for admin, analyst, reviewer, and auditor.
- Audit logs for prompts, outputs, retrieved docs, approvals, costs, and reviewer actions.
- Evaluation score.
- Review queue.
- Incident list.
- Audit log.
- Dashboard overview.
- Demo seed data.

### P1 — Should have

- Prompt versioning.
- Risk heatmap.
- Cost dashboard.
- Data source registry.
- Review detail evidence view.
- Export CSV/JSON.
- Provider adapter stubs.
- GitHub Actions.

### P2 — Nice to have

- System relationship graph.
- Governance posture score.
- Notification integrations.
- Azure OpenAI live adapter.
- Azure Content Safety live adapter.
- Application Insights telemetry.
- Entra ID auth.

### P3 — Later

- Purview metadata sync.
- Terraform/Bicep deployment.
- Multi-tenant isolation.
- Data retention engine.
- Advanced policy engine.
- Custom evaluator builder.
- Enterprise SSO/SCIM.

## YouTube series milestones

### Episode 1 — Build the AI Governance Control Tower

Show the problem, architecture, and local dashboard.

### Episode 2 — The Governance Gateway

Show how every AI request is checked, logged, and routed.

### Episode 3 — Human Review and Incidents

Show failures, review queue, and accountable decisions.

### Episode 4 — Azure Integration Plan

Show how the local architecture maps to Azure OpenAI, Content Safety, Key Vault, Monitor, Entra, and Purview.

### Episode 5 — What This Teaches About AI Governance

Reflect on limitations, risk scoring, false confidence, and operational governance.

## Project risks

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Scope creep into enterprise compliance platform | High | High | Keep MVP boundary strict. |
| Azure setup blocks progress | Medium | High | Build local-first and use adapters/stubs. |
| Dashboard becomes too generic | Medium | Medium | Follow `DESIGN.md` and review screenshots early. |
| Evaluation scores are overstated | Medium | High | Label as signals, show evidence, require human review. |
| Security features delayed | Medium | High | Implement RBAC/audit/validation early. |
| Demo data feels fake or weak | Medium | Medium | Seed realistic synthetic incidents and workflows. |

## Success criteria

The project succeeds if a viewer or reviewer can quickly understand:

- What AI systems exist.
- Who owns them.
- Which ones are risky.
- Which model runs failed checks.
- Which outputs required human review.
- What incidents occurred.
- What decisions were made.
- How the system could plug into Azure.
- Why governance is different from simply building AI apps.
