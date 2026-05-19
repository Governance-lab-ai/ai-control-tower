# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-19  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


# Evaluation Integrations

## Purpose

This document defines how the Control Tower should integrate with external evaluation, red-teaming, safety, observability, and policy tools without reinventing every specialised capability.

The Control Tower should own the governance workflow:

```text
route
  -> evaluate
  -> review
  -> incident
  -> evidence
```

It should not try to become the best tool for every evaluation problem.

## Design principle

> Build the governance orchestration layer. Integrate specialised tools where they are stronger.

The MVP can use local heuristics to demonstrate the flow. Later versions should support external evaluators through provider interfaces.

## Integration categories

| Category | Example tools | Role in Control Tower |
|---|---|---|
| LLM eval frameworks | Inspect, Dioptra, Promptfoo, Giskard, Ragas | Produce structured evaluation results |
| Red-team/security scanners | Garak, Promptfoo, Giskard | Find jailbreak, leakage, misuse, unsafe behaviour |
| Observability | Langfuse, Phoenix, OpenTelemetry | Provide traces, sessions, latency, token, cost, and debug data |
| Guardrails | Guardrails AI, NeMo Guardrails | Enforce input/output constraints |
| Safety APIs | Azure AI Content Safety, Prompt Shields, groundedness detection | Safety, jailbreak, groundedness, protected content checks |
| Fairness/explainability | Fairlearn, AI Fairness 360, InterpretML, Aequitas | Assess traditional ML or decision-support systems |
| Policy-as-code | Open Policy Agent | Execute policy decisions outside application code |

## Provider interface model

### Base evaluator interface

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any

class EvaluationContext(BaseModel):
    company_id: str
    system_id: str
    model_run_id: str | None = None
    prompt: str | None = None
    input_text: str | None = None
    output_text: str | None = None
    retrieved_documents: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {}

class EvaluationCheckResult(BaseModel):
    check_name: str
    passed: bool
    severity: str
    score: float | None = None
    categories: list[str] = []
    explanation: str
    evidence: list[dict[str, Any]] = []
    raw: dict[str, Any] = {}

class EvaluationProviderResult(BaseModel):
    provider_name: str
    provider_version: str | None = None
    overall_passed: bool
    overall_score: float | None = None
    results: list[EvaluationCheckResult]
    metadata: dict[str, Any] = {}

class EvaluationProvider(ABC):
    @abstractmethod
    async def evaluate(self, context: EvaluationContext) -> EvaluationProviderResult:
        pass
```

### Evaluation provider registry

The backend should support a registry of enabled providers.

```python
class EvaluationProviderConfig(BaseModel):
    provider_name: str
    enabled: bool
    applies_to_risk_levels: list[str]
    applies_to_system_ids: list[str] = []
    trigger_mode: str  # pre_execution, post_execution, scheduled, manual
    timeout_ms: int = 10000
    fail_closed: bool = False
    config: dict[str, Any] = {}
```

## Pre-execution vs post-execution checks

| Stage | Checks | Route impact |
|---|---|---|
| Pre-execution | Approval, role, prompt policy, PII, prompt injection, data-source permission, critical-risk gate | Allow, hold, block |
| Post-execution | Output safety, output PII, groundedness, relevance, hallucination signals, cost/latency anomaly | Allow, allow with review, hold/reject, incident |
| Scheduled | Benchmark tests, red-team suites, fairness tests, regression tests | Approval changes, incidents, control test evidence |
| Manual | Reviewer-triggered evals or incident investigations | Evidence and remediation |

## MVP local evaluators

MVP evaluators should be simple and explicit:

| Evaluator | Purpose | Limitations |
|---|---|---|
| `LocalPIIEvaluator` | Detect obvious email, phone, address, account number patterns | Misses context, false positives |
| `LocalPromptInjectionEvaluator` | Detect common jailbreak/instruction-override patterns | Weak against novel attacks |
| `LocalSafetyEvaluator` | Flag obvious harmful or policy-violating output | Not a real safety classifier |
| `LocalGroundednessEvaluator` | Estimate source support using overlap | Weak semantic signal |
| `LocalRelevanceEvaluator` | Check whether output appears related to request | Shallow heuristic |
| `LocalCostLatencyEvaluator` | Flag high cost/latency | Needs baselines |

Each MVP evaluator must include a limitation statement in the returned result.

Example:

```json
{
  "check_name": "local_prompt_injection",
  "passed": false,
  "severity": "high",
  "score": 0.92,
  "categories": ["instruction_override", "system_prompt_request"],
  "explanation": "Input contained phrases commonly associated with instruction override.",
  "limitations": "Pattern-based detector; not reliable against sophisticated prompt injection."
}
```

## External evaluator integrations

### UK AISI Inspect

Potential use:

- Scheduled eval suites.
- Behavioural evals.
- Agentic task evaluation.
- Model-graded evaluation workflows.

Control Tower role:

- Trigger Inspect evaluations.
- Store results as `external_evaluation_result`.
- Link result to system, prompt version, model, and evidence pack.

Integration mode:

```text
manual/scheduled eval run
  -> Inspect task
  -> result JSON
  -> Control Tower evaluation_result
  -> evidence_item
```

MVP status: Later.

### NIST Dioptra

Potential use:

- Reproducible AI test workflows.
- Model risk experiments.
- Robustness/security testing.
- Traditional ML testing.

Control Tower role:

- Reference Dioptra test reports as evidence.
- Store test metadata and result summaries.
- Link to control tests.

MVP status: Later.

### Promptfoo

Potential use:

- Prompt regression testing.
- Red-team testing.
- CI/CD prompt checks.
- RAG behaviour tests.

Control Tower role:

- Run Promptfoo tests for prompt versions before approval.
- Block approval if critical tests fail.
- Store test result as evidence.

MVP status: Later.

### Garak

Potential use:

- LLM vulnerability scanning.
- Probing for jailbreaks, leakage, hallucination, toxicity, malware-like behaviours, and other risks.

Control Tower role:

- Run scans against systems/providers.
- Create incidents or control-test failures for severe findings.
- Track scan history.

MVP status: Later.

### Giskard

Potential use:

- LLM application evaluation.
- Test suites for vulnerabilities and business failures.
- Model quality checks.

Control Tower role:

- Use as scheduled evaluator.
- Store output in evaluation records.

MVP status: Later.

### Ragas

Potential use:

- RAG-specific evaluation.
- Faithfulness, context precision/recall, answer relevance.

Control Tower role:

- Evaluate systems with retrieval.
- Feed groundedness and relevance scores into route decisions or periodic control tests.

MVP status: Later.

### Langfuse

Potential use:

- LLM traces.
- Sessions.
- Prompt management.
- Eval scores.
- Cost and latency monitoring.

Control Tower role:

- Either receive Langfuse trace IDs or send run metadata to Langfuse.
- Use Langfuse for engineering observability while Control Tower owns governance status, review, incident, and evidence.

Integration pattern:

```text
Application run
  -> Langfuse trace
  -> Control Tower governance run
  -> shared trace_id/model_run_id
```

MVP status: Later.

### OpenTelemetry

Potential use:

- Standard traces, logs, metrics.
- Integration with Azure Monitor/Application Insights or other observability stacks.

Control Tower role:

- Emit governance spans/events.
- Preserve trace IDs in model runs.

Suggested span names:

```text
ai_governance.gateway.pre_check
ai_governance.gateway.route_decision
ai_governance.model.execute
ai_governance.evaluation.post_check
ai_governance.review.create
ai_governance.incident.create
```

MVP status: Later.

### Open Policy Agent

Potential use:

- Policy-as-code.
- Separating policy decisions from application logic.
- Auditable policy versioning.

Control Tower role:

- Prepare policy input from system, user, prompt, data, risk, and evaluation context.
- Call OPA for decision.
- Store policy version, input hash, and decision.

Example policy input:

```json
{
  "system": {
    "risk_level": "high",
    "approval_status": "approved",
    "contains_personal_data": true
  },
  "user": {
    "role": "analyst",
    "department": "finance"
  },
  "request": {
    "pii_detected": true,
    "prompt_injection_detected": false
  }
}
```

MVP status: Later.

## Evaluation result normalization

All external provider results should be normalized into the internal `evaluation_result` model.

Suggested fields:

| Field | Meaning |
|---|---|
| `provider_name` | Source tool/provider |
| `provider_run_id` | External run identifier |
| `provider_version` | Version if available |
| `check_name` | Normalised check name |
| `raw_check_name` | Tool-specific check name |
| `passed` | Boolean pass/fail |
| `severity` | Info/low/medium/high/critical |
| `score` | Numeric if available |
| `categories` | Risk categories |
| `explanation` | Human-readable summary |
| `evidence_snippets` | Safe snippets only |
| `raw_result_ref` | Secure link/object reference to raw output |
| `limitations` | Known limitations |
| `created_at` | Timestamp |

## Evaluation categories

Use stable internal categories even when providers use different labels.

| Internal category | Examples |
|---|---|
| `pii` | Personal data detected |
| `safety` | Harmful/toxic/policy-violating content |
| `prompt_injection` | Jailbreak/instruction override |
| `data_leakage` | Sensitive info disclosure |
| `groundedness` | Unsupported claim or weak source support |
| `relevance` | Output does not answer request |
| `fairness` | Disparate impact or bias signal |
| `security` | Tool misuse, credential leakage, unsafe code |
| `cost` | Token/cost anomaly |
| `latency` | Performance anomaly |
| `policy` | Organisation policy violation |
| `quality` | Generic output quality issue |

## Evaluation routing rules

Example routing defaults:

| Condition | Route |
|---|---|
| Critical prompt injection detected pre-execution | Block |
| PII detected in input for unauthorised system | Block |
| PII detected in output | Hold for review or incident |
| Low groundedness in customer-facing answer | Allow with review or hold |
| High-risk system with failed safety check | Hold or block |
| Medium-risk system with low-severity warning | Allow with review |
| Scheduled red-team critical failure | Create incident and set system to needs changes |

## Fail-open vs fail-closed

Each evaluator should specify behaviour when unavailable.

| Context | Recommended default |
|---|---|
| Low-risk internal productivity | Fail open with warning |
| Medium-risk customer-facing | Fail open with review or hold depending on control |
| High-risk decision support | Fail closed or hold |
| Critical/prohibited use | Fail closed |

Store evaluator failures as evidence:

```text
evaluation_provider_unavailable
route_decision
audit_event
```

## CI/CD integration idea

Prompt and system changes should be testable before approval.

Example flow:

```text
prompt version changed
  -> CI/test event
  -> run promptfoo/inspect/giskard suite
  -> store control_test_result
  -> if critical fail, prevent approval
  -> if pass, attach evidence to prompt version
```

## API sketch

```text
GET /api/v1/evaluation-providers
POST /api/v1/evaluation-providers/{provider_name}/test
POST /api/v1/evaluations/run
GET /api/v1/evaluations/{evaluation_id}
GET /api/v1/systems/{system_id}/evaluation-history
```

## Integration status dashboard

Settings page should show:

| Provider | Status | Purpose |
|---|---|---|
| Local PII | Enabled | MVP checks |
| Local Prompt Injection | Enabled | MVP checks |
| Azure AI Content Safety | Not configured | Safety |
| Prompt Shields | Not configured | Prompt injection |
| Langfuse | Not configured | Tracing |
| OpenTelemetry | Not configured | Telemetry |
| Inspect | Not configured | Evaluation suite |
| Promptfoo | Not configured | Prompt regression |
| OPA | Not configured | Policy-as-code |

## Public wording guidance

Use:

> The MVP uses simple local checks to demonstrate governance flow. The architecture is designed to integrate stronger evaluation and observability tools later.

Avoid:

> Our local heuristics are enough for real assurance.

Use:

> The Control Tower is the orchestration and evidence layer, not a replacement for specialised evaluators.

Avoid:

> We are building every eval tool ourselves.

## References

- UK AISI Inspect: https://inspect.aisi.org.uk/
- NIST Dioptra: https://pages.nist.gov/dioptra/
- Promptfoo: https://www.promptfoo.dev/
- Garak: https://github.com/NVIDIA/garak
- Giskard: https://github.com/Giskard-AI/giskard
- Ragas: https://www.ragas.io/
- Langfuse: https://langfuse.com/
- OpenTelemetry: https://opentelemetry.io/
- Open Policy Agent: https://openpolicyagent.org/docs
- Azure AI Content Safety: https://learn.microsoft.com/en-us/azure/ai-services/content-safety/
