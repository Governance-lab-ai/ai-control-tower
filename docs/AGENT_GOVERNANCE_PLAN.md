# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-25  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


## Why this plan exists

The current Control Tower governs registered AI systems and model runs. The next step is to govern agent actions as well.

The direction is:

```text
System governance
  -> model-run governance
  -> policy decisions
  -> tool/action governance
  -> agent identity and capability governance
```

This is similar in spirit to emerging agent governance toolkits, but the Control Tower should stay focused on the business governance plane: owners, approvals, review workflows, incidents, audit evidence, and dashboards.

## Target business architecture

```text
Business app / agent
  -> Control Tower Gateway
  -> identity and registered AI system lookup
  -> policy decision
  -> model provider and/or tool call
  -> evidence, audit, review, incident, dashboard
```

The organisation should be able to answer:

- Which AI systems and agents exist?
- Who owns them?
- Which model providers and tools are they allowed to use?
- Which policies were active when a run or action happened?
- Why was an action allowed, denied, or sent for review?
- Which human approved or rejected risky activity?
- What evidence supports the governance decision?

## Build sequence

### 1. Policy decision layer

Status: started.

Purpose:

- Separate governance decisions from ad hoc route logic.
- Produce explicit `allow`, `deny`, and `require_review` decisions.
- Store policy name, policy version, matched rules, reasons, and safe metadata.

Current implementation:

- `LocalPolicyDecisionProvider` style service in `backend/app/services/policy_engine.py`.
- `POST /policies/evaluate` for local policy smoke tests.
- Gateway model execution now records a `policy_decision` run step.

Next improvements:

- Persist policy versions as database records.
- Store policy version ID on model runs and audit events.
- Add a policy page to inspect active policies and matched rules.
- Later integrate OPA/Rego, Cedar, or another mature policy engine rather than inventing a large custom language.

### 2. Agent and capability registry

Purpose:

- Register autonomous or semi-autonomous agents separately from AI systems.
- Define which models, tools, data sources, and actions each agent can use.

Minimum records:

- `agents`: name, owner, department, purpose, risk level, status, linked AI system.
- `tools`: name, category, risk level, integration type, write/read capability.
- `agent_capabilities`: agent ID, tool ID, allowed actions, approval requirement.

Example:

```text
Support Triage Agent
  allowed model: llama3.2 / Azure OpenAI support deployment
  allowed tools: ticket_read, knowledge_search
  restricted tools: send_email requires review
  blocked tools: delete_ticket, refund_payment
```

### 3. Tool-call governance endpoint

Purpose:

- Govern every tool action before an agent executes it.

Target endpoint:

```text
POST /governance/tool-call
```

Request:

```json
{
  "agent_id": "agent_123",
  "actor": "service:support-agent",
  "tool_name": "send_email",
  "action": "send",
  "arguments": {
    "to": "synthetic@example.test"
  },
  "metadata": {
    "source_app": "support-console"
  }
}
```

Response:

```json
{
  "status": "requires_review",
  "policy_name": "local-governance-policy",
  "policy_version": "2026.05.local-v1",
  "matched_rules": ["review-high-impact-tool"],
  "reasons": ["Tool send_email requires human review before execution."],
  "audit_event_id": "..."
}
```

### 4. MCP and external tool boundary

Purpose:

- Make MCP/tool integrations observable and enforceable.
- Prevent hidden tool use outside the gateway.

Controls:

- Tool registry.
- Tool allowlists.
- Argument validation.
- Read/write distinction.
- High-impact action review.
- Tool-call audit events.
- Tool poisoning / hidden instruction checks later.

### 5. Agent identity and trust

Purpose:

- Stop treating all actions as `"local:operator"` or shared API keys.

Near-term:

- Mock service accounts.
- Actor type: `user`, `service`, `agent`.
- Department and role metadata.

Later:

- Microsoft Entra ID.
- Workload identity.
- mTLS or signed agent identity.
- Per-agent credentials and capability grants.

### 6. Evidence and reporting

Purpose:

- Make agent governance explainable to security, risk, governance, and audit teams.

Evidence objects:

- Model run.
- Tool call.
- Policy decision.
- Human review.
- Incident.
- Audit event.

Dashboards:

- Agents by department and risk.
- Tool calls by action.
- Denied actions.
- Review-required actions.
- High-impact tool usage.
- Incidents by agent/system.

## Implementation principles

- Keep all provider/tool calls backend-only.
- Do not expose provider secrets or tool credentials to frontend code.
- Policy decisions must be explicit and logged.
- Human review should be a first-class workflow, not a comment field.
- Avoid storing unnecessary sensitive values in audit events.
- Use controlled evidence records for prompts, outputs, retrieved documents, and tool arguments.
- Prefer integration with mature policy/security tools over inventing a large policy language.

## Immediate next episodes

1. **Episode 8: Policy and Capability Engine**
   - Persist policies and policy decisions.
   - Add agent/tool/capability registry tables.
   - Add frontend pages for policies, agents, and tools.

2. **Episode 9: Tool-Call Governance**
   - Add `/governance/tool-call`.
   - Record tool-call evidence.
   - Enforce allow/deny/review rules.

3. **Episode 10: Identity and RBAC**
   - Add user/service/agent actors.
   - Enforce admin, analyst, reviewer, auditor permissions.
   - Prepare Entra ID integration.

4. **Episode 11: Integration Hardening**
   - Add provider settings and health checks.
   - Add OPA/Rego or equivalent policy provider option.
   - Add MCP security gateway design.
