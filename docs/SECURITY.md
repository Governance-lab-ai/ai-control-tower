# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-12  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


## Security objective

The Control Tower handles sensitive governance data: prompts, inputs, outputs, retrieved documents, review decisions, model metadata, costs, user identities, and audit logs. The system must be designed as if prompts and outputs may contain confidential or personal data.

Security goal:

> Make the secure path the default path. Model execution, review, incident handling, and audit logging should be controlled, observable, and permissioned from the beginning.

## Security reference anchors

Use these as guidance anchors, not as box-ticking checklists:

- OWASP Top 10 for LLM Applications.
- OWASP Web Application Security Top 10.
- NIST AI Risk Management Framework.
- Microsoft cloud security guidance for Entra ID, Key Vault, Azure Monitor, and AI services.

## Assets to protect

| Asset | Why it matters |
|---|---|
| Prompts and inputs | May contain confidential business data or personal data. |
| Model outputs | May contain generated sensitive data, hallucinations, or policy violations. |
| Retrieved documents | May include internal knowledge base, support, CRM, or product docs. |
| AI system registry | Contains ownership, risk, model, and data-source metadata. |
| Evaluation results | Reveals failures, sensitive classifications, and risk posture. |
| Human review decisions | Accountability and potential legal/business evidence. |
| Audit logs | Integrity-critical evidence trail. |
| API keys and secrets | Access to models, data sources, and cloud resources. |
| User identities and roles | Control who can approve, review, export, and configure systems. |
| Integration configuration | Cloud/resource metadata and service endpoints. |

## Threat model summary

### Main attacker types

- Unauthenticated external attacker.
- Authenticated low-privilege user.
- Malicious or careless internal user.
- Compromised integration/API key.
- Prompt injection attacker through user input or retrieved documents.
- Supply-chain attacker through dependencies or model/tool integrations.

### Main threat categories

| Threat | Example | Control |
|---|---|---|
| Unauthorised access | User sees HR AI system data. | Auth, RBAC, tenant isolation, object-level permissions. |
| Prompt injection | Input asks model to ignore system instructions or reveal secrets. | Prompt policy checks, Prompt Shields later, strict tool boundaries. |
| Sensitive data leakage | Output includes email, payment data, support ticket content. | PII detection, redaction, review routing, retention controls. |
| Insecure output handling | Model output rendered as HTML/JS. | Escape output, no raw HTML, content security policy. |
| Model denial of service | Excessive prompts or long context drives cost/latency. | Rate limits, token budgets, request size limits. |
| Data-source overreach | System retrieves documents it should not access. | Data source ACLs, retrieval permission checks, metadata logging. |
| Audit tampering | User deletes bad run or changes decision. | Append-only audit events, restricted admin actions. |
| Secret exposure | API key in frontend or logs. | Server-only secrets, Key Vault later, redaction. |
| Supply chain | Vulnerable dependency or malicious package. | Lockfiles, scans, minimal dependencies, CI checks. |
| Misleading evaluation | Score implies compliance/safety certainty. | Explain limits, show evidence, require human review. |

## Authentication and authorization

### MVP

- Use mocked users only for local demo.
- Implement role checks in backend even before real auth.
- Roles should be attached to API requests through a controlled dev header or local session mechanism.
- Never let frontend-only state decide permissions.

### Suggested roles

| Role | Permissions |
|---|---|
| Admin | Manage systems, approvals, policies, users, exports, integrations, and settings. |
| Analyst | Read dashboards, registry data, runs, evaluations, incidents, costs, and latency metrics. |
| Reviewer | View review queue, inspect permitted run evidence, and make review decisions. |
| Auditor | Read-only access to audit logs, evidence summaries, approvals, reviewer actions, and exports. |

Optional future roles can split admin duties into system owner, governance admin, and security admin, but the MVP access model should start with `admin`, `analyst`, `reviewer`, and `auditor`.

### Azure target

- Use Microsoft Entra ID for identity.
- Map Entra groups to application roles.
- Use backend-enforced RBAC.
- Use managed identities for Azure resource access.

## Secrets management

### Local

- Store secrets in `.env.local` or backend `.env` files.
- `.env*` files with real values must be gitignored.
- Provide `.env.example` only.
- Never expose LLM, Azure, DB, or integration keys to Next.js public variables.

### Azure

- Store secrets in Azure Key Vault.
- Use managed identity where possible.
- Avoid long-lived client secrets.
- Rotate secrets.
- Log access to secrets.

## Data classification

Classify records by sensitivity:

| Classification | Examples | Handling |
|---|---|---|
| Public demo | Synthetic seed data | Can appear in screenshots. |
| Internal metadata | System names, departments, owners | Authenticated access. |
| Confidential | Prompts, outputs, retrieved docs | Restricted access, redaction, retention. |
| Personal data | Emails, names, phone, addresses, ticket content | PII flags, redaction, review, strict retention. |
| Security-sensitive | API keys, auth tokens, system prompts | Never log, never expose to frontend. |

## Logging rules

Do log:

- Request IDs.
- User ID / actor ID.
- System ID.
- Run ID.
- Route decision.
- Evaluation categories.
- Severity.
- Latency.
- Cost.
- Provider/model version.

Do not log to application logs by default:

- Full prompts.
- Full inputs.
- Full outputs.
- Raw retrieved documents.
- Secrets.
- Access tokens.
- PII values.

Store sensitive content only in controlled database fields with permissions and retention policies.

## Audit log rules

Audit events should be append-only and include:

- Actor.
- Action.
- Entity type.
- Entity ID.
- Timestamp.
- Before/after state where safe.
- Reason.
- Source IP/user agent where appropriate.
- Request ID.

Sensitive values in before/after state should be redacted.

Critical actions requiring audit events:

- AI system created/updated/deleted/retired.
- Approval status changed.
- Prompt submitted to the governance gateway.
- Model output produced by the provider.
- Retrieved documents attached to a run.
- Prompt version created/activated/deactivated.
- Model run executed, blocked, or held.
- Cost or token estimate captured.
- Evaluation failure.
- Review decision.
- Reviewer action or comment added.
- Incident created/updated/resolved.
- Export generated.
- Integration settings changed.
- Role/permission changed.

Audit records should track prompts, outputs, retrieved docs, approvals, costs, and reviewer actions. Sensitive prompt/output/document content should be stored as controlled evidence with redacted audit metadata, not copied into general logs.

## Input validation

Backend:

- Pydantic schemas for all requests.
- Enforce max length on prompt/input/output fields.
- Validate enums strictly.
- Validate UUIDs.
- Validate date ranges.
- Validate pagination and filters.
- Reject unknown dangerous fields where appropriate.

Frontend:

- Zod schemas for forms.
- Client-side validation for UX only.
- Backend remains source of truth.

## Output handling

- Treat model output as untrusted content.
- Render as escaped text or markdown through a safe renderer.
- Disable raw HTML rendering by default.
- Use a strict Content Security Policy.
- Do not insert model output into `dangerouslySetInnerHTML`.
- Flag links in outputs.
- For code output, display as text unless explicitly handled.

## LLM-specific controls

### Prompt injection

Controls:

- Pre-check user prompts and retrieved documents.
- Detect jailbreak language and attempts to override system/developer instructions.
- Detect suspicious prompt heuristics such as requests to reveal hidden prompts, bypass policy, ignore prior instructions, or exfiltrate context.
- Separate system instructions from user input.
- Do not expose hidden system prompts.
- Do not allow model output to directly trigger privileged actions.
- Validate tool calls server-side.
- Use strict allowlists for tools and data sources.
- Enforce tool restriction logic before execution and block unapproved tool instructions.
- Add Prompt Shields in Azure phase.

### Sensitive information disclosure

Controls:

- PII detection before and after generation using Presidio/Microsoft Presidio where available.
- Use regex, NER, and entity detection fallback in local/demo mode.
- Detect at minimum names, emails, phone numbers, account numbers, addresses, and payment-card-like values where practical.
- Redact names, emails, phone numbers, and account numbers before LLM execution when the policy requires it.
- Redact previews in UI where appropriate.
- Route sensitive outputs to review.
- Prevent reviewers from exporting data unless authorised.
- Avoid sending unnecessary context to LLMs.

Episode 5 local implementation:

- Uses `HybridLocalPIIDetector` for synthetic demo patterns and obvious structured values only.
- Detects emails, phone numbers, labelled names, labelled account IDs, labelled addresses, labelled dates of birth, labelled national IDs, labelled postal codes, spaced IBAN-like values, and Luhn-valid payment-card-like values.
- Stores detector results with redacted snippets and confidence labels.
- Creates PII incidents for detected input/output PII.
- Is not comprehensive and must not be represented as legal, privacy, or regulatory assurance.

V2/Azure improvements should add Presidio/Microsoft Presidio, NER, Azure AI services, and policy-specific recognizers behind the same detector interface.

### Excessive agency

Controls:

- MVP should not allow autonomous external actions.
- If tools are added, require explicit tool permission and logging.
- High-risk tools require human approval.
- Limit tool scope and validate arguments.

### Model denial of service

Controls:

- Rate limits by user/system/company.
- Token budgets.
- Request size limits.
- Timeout limits.
- Cost thresholds.
- Queueing for expensive evaluation.

### RAG and retrieval risks

Controls:

- Register data sources.
- Attach system permissions to data sources.
- Store document metadata for retrieved docs.
- Check document sensitivity.
- Treat retrieved documents as potentially prompt-injected.
- Do not retrieve documents from unapproved sources.

## API security

- Use HTTPS in deployed environments.
- Add CORS allowlist.
- Use secure cookies if cookie-based auth is used.
- CSRF protection for state-changing browser requests if cookies are used.
- Use bearer-token validation if token auth is used.
- Enforce backend RBAC for every endpoint.
- Use pagination for list endpoints.
- Use rate limiting.
- Return stable error codes without leaking secrets.

## Database security

- Use least-privilege DB user.
- Use migrations.
- Use parameterised queries through ORM.
- Do not allow arbitrary SQL from users.
- Back up database in deployed environments.
- Consider row-level isolation for multi-tenant production.
- Consider partitioning or retention for model runs.

## Frontend security

- No public LLM keys.
- No raw HTML rendering of model outputs.
- Use Content Security Policy.
- Avoid leaking sensitive data into browser local storage.
- Use secure HTTP-only cookies if cookie-based auth is used.
- Hide actions the user cannot take, but also enforce server-side.
- Do not display full PII by default; use reveal controls for authorised reviewers.

## CI/CD security

Baseline checks:

- Backend lint.
- Backend tests.
- Frontend lint.
- Frontend tests.
- Type checks.
- Dependency vulnerability scan.
- Secret scan.
- Container scan if building images.

Pull request checklist:

- Does this add a new route?
- Does the route enforce permissions?
- Does it create audit events for state changes?
- Does it handle sensitive data safely?
- Does it add tests?
- Does it require a schema migration?
- Does it update docs?

## Incident response inside the product

Incident states:

- `open`
- `investigating`
- `resolved`
- `dismissed`
- `escalated`

Incident severities:

- `low`
- `medium`
- `high`
- `critical`

Incident records should include:

- Type.
- Severity.
- Status.
- AI system.
- Model run.
- Detection reason.
- Owner.
- Created timestamp.
- Resolution timestamp.
- Resolution notes.
- Linked audit events.

## Secure defaults

Default to:

- Systems start as pending, not approved.
- New prompt versions start inactive/pending.
- Unknown risk routes to review.
- Missing safety result routes to review for medium/high systems.
- Failed audit logging blocks critical state changes.
- Export requires elevated permission.
- Raw sensitive values are hidden unless explicitly revealed by authorised users.

## Security acceptance criteria for MVP

The MVP should not ship publicly unless:

- There are no real secrets in the repo.
- The local demo uses synthetic data only.
- Backend enforces role checks for review, approval, incident, and export actions.
- Model execution through the gateway creates model run, evaluation, and audit records.
- Unapproved systems cannot execute.
- Model output is safely rendered.
- Critical state changes generate audit events.
- Basic rate limiting or request-size limits exist.
- Security limitations are documented.

## Known limitations for MVP

- Local PII detection will be imperfect.
- Local groundedness heuristic will not prove truth.
- Mock auth is not production auth.
- Local logs are not enterprise telemetry.
- Audit events are append-only by application convention, not cryptographically immutable.
- Multi-tenant hardening is not complete unless explicitly implemented.

These limitations should be visible in docs and demos.
