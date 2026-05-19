# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-19  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


# Competitive Landscape

## Purpose

This document explains where the AI Governance Control Tower fits relative to existing AI governance frameworks, testing tools, observability platforms, and enterprise governance products.

The goal is not to claim that no AI governance tooling exists. It does. The goal is to define the project's lane clearly:

> **The AI Governance Control Tower is an open, local-first, engineer-readable reference implementation of runtime AI governance.**

It shows how policy intent can become operational controls, routing decisions, human review workflows, incidents, audit events, and evidence.

## Positioning summary

The market already contains useful frameworks and tools:

- Governance frameworks explain what good governance should include.
- Testing and evaluation tools help measure model and system behaviour.
- Observability tools trace prompts, completions, costs, latency, and failures.
- Guardrail tools enforce input/output constraints.
- Policy-as-code tools make rules executable.
- Enterprise governance platforms manage inventory, risks, evidence, workflows, and audits.

The Control Tower should not pretend these do not exist.

The stronger thesis is:

> **The pieces exist, but the bridge between AI governance language and runtime engineering is still hard to see. This project makes that bridge visible in code.**

## What this project is

The Control Tower is:

- A reference architecture for operational AI governance.
- A demoable implementation of a governed model gateway.
- A local-first teaching and prototyping system.
- A system for showing how AI inventory, risk routing, evaluations, human review, incidents, and audit evidence can connect.
- A practical companion to frameworks such as NIST AI RMF, ISO/IEC 42001, the EU AI Act, OECD AI Principles, and OWASP guidance.
- A place to test assumptions about what evidence AI governance actually needs.

## What this project is not

The Control Tower is not:

- A legal compliance product.
- A certification engine.
- A replacement for legal, privacy, security, risk, or compliance review.
- A full enterprise GRC platform.
- A model evaluation benchmark suite.
- A standalone LLM observability product.
- A guarantee that an AI system is safe, fair, lawful, or compliant.
- A substitute for human accountability.

## Landscape map

| Category | Examples | What they provide | How the Control Tower should relate |
|---|---|---|---|
| Governance frameworks | NIST AI RMF, ISO/IEC 42001, OECD AI Principles, EU AI Act | Concepts, obligations, risk management structure, management-system expectations | Map their ideas to concrete controls, evidence, and workflows |
| Governance testing / assessment | AI Verify | Process checks, technical tests, reports, framework mappings | Treat as a complementary assessment/reporting layer |
| AI evaluation frameworks | NIST Dioptra, UK AISI Inspect, Project Moonshot | Reproducible model/system evaluations and red-teaming workflows | Integrate as evaluator plugins or use as reference patterns |
| LLM observability | Langfuse, Arize Phoenix, OpenTelemetry-based tracing | Traces, sessions, prompt/completion logs, metrics, cost, latency, debugging | Integrate rather than recreate all tracing functionality |
| LLM eval / red-team tools | Promptfoo, Giskard, Garak, Ragas | Prompt tests, RAG evals, attack probes, red-team suites | Use as optional evaluation providers |
| Guardrails | NVIDIA NeMo Guardrails, Guardrails AI | Input/output validation and behavioural constraints | Treat as pre/post execution control providers |
| Policy-as-code | Open Policy Agent | Declarative policy decisions separated from enforcement | Use as a future policy decision layer |
| Fairness / explainability | Fairlearn, IBM AI Fairness 360, InterpretML, Aequitas | Bias assessment, mitigation, explainability, model diagnostics | Integrate for traditional ML and decision-support systems |
| Documentation | Model Cards, Datasheets for Datasets | Structured transparency records | Connect documentation to evidence and control history |
| Enterprise AI governance platforms | VerifyWise, Credo AI, Holistic AI, others | AI inventory, risk workflows, evidence, policy packs, assessments, audit readiness | Do not compete head-on in MVP; differentiate as public reference implementation |

## Differentiation

The strongest differentiation is not "we have a dashboard."

Dashboards are common.

The differentiator is the runtime chain:

```text
AI system registry
  -> approval state
  -> governed model gateway
  -> pre-execution checks
  -> route decision
  -> model execution
  -> post-execution evaluations
  -> human review or incident
  -> audit evidence
  -> dashboard and export
```

The project becomes valuable when it can show exactly where governance evidence is generated.

## Primary product thesis

> You cannot govern what you cannot see.

A serious AI governance system needs to answer:

- What AI systems exist?
- Who owns them?
- What are they allowed to do?
- What risk category are they in?
- What data do they use?
- Were they approved?
- What happened at runtime?
- Which checks ran?
- What failed?
- Who reviewed it?
- What decision was made?
- What evidence exists later?

## Avoiding weak claims

Do not say:

> Nobody has built AI governance tooling.

Say:

> A lot of useful tooling exists, but it is fragmented across frameworks, evals, observability, guardrails, GRC, and documentation. The Control Tower explores how those pieces can connect into a runtime governance workflow.

Do not say:

> This makes AI compliant.

Say:

> This generates operational evidence that may support governance, assurance, audit readiness, and internal accountability.

Do not say:

> This detects all harmful AI behaviour.

Say:

> This applies configurable signals and controls, then routes uncertainty to people when risk is high.

## Build-vs-integrate principles

The Control Tower should build the minimum needed to demonstrate the governance workflow, then integrate with better specialised tools later.

| Capability | MVP approach | Later approach |
|---|---|---|
| PII detection | Regex/heuristics | Presidio, cloud safety services, custom classifiers |
| Safety checks | Local heuristics | Azure AI Content Safety, Guardrails AI, NeMo Guardrails |
| Prompt injection checks | Pattern rules | LLM security scanners, Prompt Shields, specialised classifiers |
| Groundedness | Source-overlap heuristic | Dedicated groundedness services, RAG evaluation tools |
| LLM tracing | Local model run records | Langfuse, Phoenix, OpenTelemetry |
| Evaluations | Local evaluators | Inspect, Dioptra, Promptfoo, Giskard, Ragas |
| Policy decisions | Python rules | OPA/Rego or other policy-as-code engine |
| Evidence export | CSV/JSON | Auditor-facing evidence packs and signed exports |
| Identity | Local mock users | Microsoft Entra ID / SSO |
| Data governance | Local data source metadata | Purview or equivalent catalogue |

## Strategic lane

The public message should be:

> **Governance Lab is building a public reference implementation of the operational layer around AI systems: registry, gateway, evaluations, human review, incidents, and audit evidence.**

That lane is credible because it is specific, buildable, and complementary to existing work.

## References

These references are anchors for comparison and should be verified before external claims:

- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI RMF Core: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
- EU AI Act service desk: https://ai-act-service-desk.ec.europa.eu/en/ai-act/
- ISO/IEC 42001: https://www.iso.org/standard/42001
- OECD AI Principles: https://oecd.ai/en/ai-principles
- AI Verify Foundation: https://aiverifyfoundation.sg/
- NIST Dioptra: https://pages.nist.gov/dioptra/
- UK AISI Inspect: https://inspect.aisi.org.uk/
- Langfuse: https://langfuse.com/
- OpenTelemetry: https://opentelemetry.io/
- Open Policy Agent: https://openpolicyagent.org/docs
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
