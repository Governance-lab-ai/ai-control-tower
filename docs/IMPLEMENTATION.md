# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-12  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


## Implementation goal

Build a local-first, Azure-aware AI governance platform with a Next.js dashboard and FastAPI backend.

The first implementation should prove the workflow, not every enterprise integration:

1. Register AI systems.
2. Approve or block systems.
3. Route model calls through a governance gateway.
4. Log every model run.
5. Run pre-execution and post-execution checks.
6. Route risky cases into human review.
7. Show the organisation's AI risk posture in a secure, command-centre-style dashboard.

V2 should evolve this into a genuine multi-agent governance system, but the MVP should first prove the gateway, registry, review, audit, and reporting workflow with bounded services.

## Non-negotiable engineering principles

- **Local-first:** the app must run locally with Docker Compose and synthetic data.
- **Azure-aware:** all major dependencies should sit behind provider interfaces so Azure services can replace local implementations later.
- **No secrets in frontend:** model/API/secrets stay server-side.
- **Synthetic demo data only:** never require real customer data for development or demos.
- **Audit everything:** approval changes, model runs, incidents, human reviews, and policy changes must generate audit events.
- **Governance gateway first:** model execution should go through the backend gateway, not directly from the frontend.
- **Provider abstraction:** avoid hard-coding OpenAI, Azure, Anthropic, or local models into business logic.
- **Typed contracts:** Pydantic on backend, TypeScript/Zod on frontend.

## Recommended repository structure

```text
ai-governance-control-tower/
  README.md
  IMPLEMENTATION.md
  ARCHITECTURE.md
  DESIGN.md
  ROADMAP.md
  SECURITY.md
  AGENTS.md
  DATA_MODEL.md
  API_SPEC.md
  AZURE_INTEGRATION.md
  GOVERNANCE_MODEL.md
  TESTING.md
  ENVIRONMENT.md

  backend/
    app/
      main.py
      api/
        routes/
          ai_systems.py
          model_runs.py
          evaluations.py
          reviews.py
          incidents.py
          audit_logs.py
          dashboard.py
      core/
        config.py
        security.py
        logging.py
        errors.py
      db/
        session.py
        base.py
        migrations/
      models/
        company.py
        user.py
        ai_system.py
        prompt_version.py
        model_run.py
        evaluation.py
        review.py
        incident.py
        audit_event.py
      schemas/
        ai_system.py
        model_run.py
        evaluation.py
        review.py
        incident.py
        audit.py
      services/
        governance_gateway.py
        risk_engine.py
        review_router.py
        cost_estimator.py
        seed_data.py
        llm/
          base.py
          mock.py
          openai_provider.py
          azure_openai.py
        safety/
          base.py
          local_pii.py
          presidio_pii.py
          local_prompt_policy.py
          redaction.py
          azure_content_safety.py
        retrieval/
          base.py
          mock.py
        audit/
          base.py
          postgres.py
        telemetry/
          base.py
          console.py
          azure_monitor.py
        secrets/
          base.py
          env.py
          azure_key_vault.py
      tests/
        unit/
        integration/
        fixtures/
    pyproject.toml
    Dockerfile

  frontend/
    app/
      layout.tsx
      page.tsx
      dashboard/page.tsx
      systems/page.tsx
      systems/new/page.tsx
      systems/[id]/page.tsx
      reviews/page.tsx
      reviews/[id]/page.tsx
      incidents/page.tsx
      incidents/[id]/page.tsx
      evaluations/page.tsx
      cost/page.tsx
      audit/page.tsx
      settings/page.tsx
    components/
      layout/
      command-center/
      charts/
      risk/
      tables/
      forms/
      review/
      audit/
    lib/
      api.ts
      types.ts
      validators.ts
      formatters.ts
      constants.ts
    hooks/
    styles/
    tests/
    package.json
    Dockerfile

  infra/
    docker-compose.yml
    azure/
      README.md
      container-apps.bicep
      postgres.bicep
      keyvault.bicep
      app-insights.bicep

  scripts/
    seed_demo_data.py
    export_audit_logs.py
    run_local_checks.sh
```

## Local development stack

### Backend

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- pytest
- ruff
- mypy or pyright
- structlog or standard logging with JSON formatting

### Frontend

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui components, customised to the design system
- TanStack Table
- Recharts, Nivo, ECharts, or Visx for dashboards
- React Hook Form + Zod
- Playwright for E2E
- Vitest/React Testing Library for component tests

### DevOps

- Docker Compose for local services
- GitHub Actions for lint/test/build
- Optional: Trivy for container/dependency scanning
- Optional: pre-commit hooks

## Local environment setup

### Prerequisites

```text
Docker Desktop or Docker Engine
Python 3.12+
Node.js current LTS
pnpm or npm
PostgreSQL client tools optional
```

### Local startup flow

```bash
# 1. Copy environment files
cp .env.example .env.local
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 2. Start local infrastructure
cd infra
docker compose up -d postgres

# 3. Start backend
cd ../backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
alembic upgrade head
python scripts/seed_demo_data.py
uvicorn app.main:app --reload --port 8000

# 4. Start frontend
cd ../frontend
pnpm install
pnpm dev
```

Expected local URLs:

```text
Frontend: http://localhost:3000
Backend:  http://localhost:8000
OpenAPI:  http://localhost:8000/docs
Postgres: localhost:5432
```

## Backend implementation phases

### Phase A — Foundation

Build:

- FastAPI app shell.
- Health endpoint.
- Config module.
- Postgres connection.
- SQLAlchemy models.
- Alembic migrations.
- Seed data script.
- JSON error format.
- Basic audit event service.

Acceptance criteria:

- `GET /health` returns app and DB status.
- Alembic migrations create all MVP tables.
- Seed data creates demo company, users, systems, runs, incidents, and reviews.
- No endpoint requires live LLM keys for the local demo.

### Phase B — AI systems registry

Build endpoints:

```text
POST   /api/v1/ai-systems
GET    /api/v1/ai-systems
GET    /api/v1/ai-systems/{system_id}
PATCH  /api/v1/ai-systems/{system_id}
PATCH  /api/v1/ai-systems/{system_id}/approval-status
GET    /api/v1/ai-systems/{system_id}/audit
```

Acceptance criteria:

- A user can create a system with owner, department, model, data sources, risk level, personal data flag, oversight flag, and approval status.
- Approval changes produce audit events.
- System detail returns related prompt versions, data sources, recent runs, reviews, and incidents.

### Phase C — Governance gateway

Build core endpoint:

```text
POST /governance/run
```

The gateway must:

1. Validate the AI system exists.
2. Verify approval status.
3. Verify user role and department permission.
4. Load approved prompt version.
5. Run prompt/input checks.
6. Run PII detection.
7. Run retrieval permission checks if documents are included.
8. Redact configured sensitive entities before provider execution.
9. Calculate dynamic risk.
10. Allow, block, or hold the request.
11. Execute LLM call if allowed.
12. Run post-execution checks.
13. Log the model run.
14. Create evaluation result.
15. Create review item or incident if needed.
16. Return final route result.

Acceptance criteria:

- Unapproved systems cannot execute.
- Blocked prompt policy creates a blocked run and audit event.
- PII in input or output is flagged.
- Names, emails, phone numbers, and account numbers can be redacted before LLM execution.
- Prompt injection, jailbreak, and suspicious tool-use attempts are visible in route reasons.
- Risky responses route to human review.
- All gateway decisions are explainable in the returned JSON.

Episode 4 logging additions:

- Executed gateway calls create `model_runs` records.
- Blocked and pending gateway calls create model-run shell records for audit review.
- Gateway execution measures latency in milliseconds.
- Local mock provider cost is estimated from prompt/input/output/retrieval text length.
- Supplied retrieved documents are persisted and linked to the run.
- `GET /model-runs`, `GET /model-runs/{run_id}`, and `GET /ai-systems/{system_id}/runs` expose run evidence for UI and review.
- `GET /ai-systems/{system_id}/prompt-versions`, `POST /ai-systems/{system_id}/prompt-versions`, and `PATCH /prompt-versions/{prompt_version_id}/activate` manage prompt versions.

Episode 5 PII and incident additions:

- `PIIDetector` interface and `HybridLocalPIIDetector` implementation.
- Input and output PII checks run in the governance gateway.
- PII incidents are created for detected input/output PII.
- Runs with detected PII are marked `requires_review`.
- `/incidents` and `/ai-systems/{system_id}/incidents` expose incident evidence to the frontend.
- Local detection uses free deterministic recognizers, label-aware rules, redaction, and Luhn validation for card-like values. It is not comprehensive.

Episode 6 evaluation additions:

- `EvaluationProvider` interface and `LocalEvaluationProvider` implementation.
- Every executed gateway call queues asynchronous evaluation after creating the `model_runs` record.
- Evaluation records include overall score, relevance score, groundedness score, hallucination flag, summary, threshold, and review requirement.
- Medium, high, and critical risk systems use stricter configurable thresholds.
- Runs with failed evaluations are marked `requires_review` by the background task.
- `/evaluations?failed_only=true` exposes failed evaluation signals to the frontend.
- `OllamaLLMProvider` can be enabled with `LLM_PROVIDER=ollama` when a local Ollama service is available.

### Phase D — Evaluation layer

Implement local evaluators first:

- PII detection using Microsoft Presidio/Presidio where available.
- Regex, NER, and entity detection fallback for local/demo mode.
- Prompt injection keyword/pattern check.
- Jailbreak detection and suspicious prompt heuristics.
- Tool restriction logic that validates allowed tools and blocks unapproved tool instructions.
- Pre-LLM redaction for names, emails, phone numbers, and account numbers.
- Output safety heuristic.
- Groundedness heuristic using retrieved source overlap.
- Relevance heuristic.
- Cost and latency capture.
- Overall evaluation score.

Do not present these as perfect. They are MVP governance signals.

Acceptance criteria:

- Every executed run queues an evaluation record.
- Evaluation result contains enough detail for human reviewers.
- Evaluation thresholds are configurable.

### Role-based access levels

The MVP role model should be simple and backend-enforced:

| Role | Purpose |
|---|---|
| `admin` | Manage systems, approvals, policies, users, exports, and settings. |
| `analyst` | View dashboards, systems, runs, evaluations, incidents, and cost/latency trends. |
| `reviewer` | Work review queues, inspect allowed evidence, and record review decisions. |
| `auditor` | Read audit logs, evidence summaries, and exports without changing operational state. |

Frontend controls may hide actions, but backend dependencies must enforce the permission checks.

### Audit evidence requirements

Audit and run evidence must cover:

- Prompts.
- Outputs.
- Retrieved documents and retrieval metadata.
- Approval changes.
- Costs and latency.
- Reviewer actions.

Full prompts, outputs, and documents should not be written to general application logs. Store them in controlled model-run/evidence records with redaction, retention, and role-based access.

## V2 multi-agent architecture

V2 should turn the gateway-led MVP into a genuine multi-agent governance system. These agents are bounded backend services, not unsupervised autonomous actors. Each agent needs typed contracts, explicit permissions, clear failure behavior, and audit events.

| Agent | Responsibilities |
|---|---|
| Retrieval Agent | Semantic retrieval, hybrid retrieval, reranking, source grounding. |
| Evaluation Agent | Hallucination scoring, groundedness, policy validation, confidence scoring. |
| Compliance Agent | PII detection, policy checks, prompt injection detection, output sanitisation. |
| Human Review Agent | Escalate risky outputs, route to reviewer, generate audit summary, maintain approval workflow. |
| Reporting Agent | Telemetry, cost tracking, latency metrics, weekly insights. |

V2 implementation should preserve the same gateway boundary: AI apps still call the Control Tower, and no frontend path may call model providers directly.

### Phase E — Review and incidents

Build:

```text
GET   /api/v1/reviews
GET   /api/v1/reviews/{review_id}
PATCH /api/v1/reviews/{review_id}/decision
GET   /api/v1/incidents
GET   /api/v1/incidents/{incident_id}
PATCH /api/v1/incidents/{incident_id}
```

Acceptance criteria:

- A reviewer can approve, reject, escalate, or request changes.
- Review decisions are logged in audit events.
- Incidents can be opened, investigated, resolved, or dismissed.

### Phase F — Dashboard APIs

Create aggregated backend endpoints rather than forcing the frontend to compute everything:

```text
GET /api/v1/dashboard/overview
GET /api/v1/dashboard/risk-heatmap
GET /api/v1/dashboard/model-runs-trend
GET /api/v1/dashboard/cost-summary
GET /api/v1/dashboard/evaluation-failures
GET /api/v1/dashboard/incidents-summary
GET /api/v1/dashboard/review-queue-summary
```

Acceptance criteria:

- Dashboard loads without N+1 API calls.
- Aggregates are consistent with underlying tables.
- Frontend can be developed using mocked API responses first.

## Frontend implementation phases

### Phase A — App shell

Build:

- Dark command-centre layout.
- Collapsible left navigation.
- Header with current company, user role, date range.
- Global loading, empty, and error states.
- Design tokens in Tailwind config.

### Phase B — Overview dashboard

Build:

- Risk posture summary.
- AI systems count.
- Model runs count.
- Failed evaluations count.
- PII incidents count.
- Cost card.
- Risk heatmap.
- Model runs trend.
- Recent incidents panel.
- Human review queue card.

### Phase C — AI systems registry

Build:

- Registry table.
- Filters by department, risk, status, owner, data sensitivity.
- New system form.
- System detail page with tabs.

### Phase D — Review queue

Build:

- Queue list.
- Review detail page/drawer.
- Input/output comparison.
- Highlighted PII and risk flags.
- Approve/reject/escalate actions.

### Phase E — Incidents and audit

Build:

- Incident table and detail page.
- Audit log table.
- Export filters.
- CSV/JSON export trigger.

### Phase F — Settings/integrations

Build cards for:

- Azure OpenAI.
- Azure AI Content Safety.
- Microsoft Purview.
- Azure Monitor/Application Insights.
- Microsoft Entra ID.
- Zendesk/CRM/Product Docs demo connections.

For MVP, cards can show local status and future Azure setup requirements.

## Provider interfaces

### LLM provider

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class LLMRequest(BaseModel):
    system_id: str
    prompt: str
    input_text: str
    model_name: str | None = None
    retrieved_documents: list[dict] = []

class LLMResponse(BaseModel):
    output_text: str
    provider: str
    model_version: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None
    latency_ms: int

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        pass
```

Current implementation:

- `LocalMockLLMProvider` is active for local deterministic demos.
- `AzureOpenAIProvider` is a placeholder and intentionally does not require credentials.

Planned provider adapters:

- `OllamaLLMProvider` for local model execution through an Ollama HTTP endpoint.
- `OpenAILLMProvider` for direct OpenAI API experiments when explicitly configured.
- `AzureOpenAIProvider` for the Azure integration phase.

All provider adapters must return normalized provider metadata, token/cost/latency information where available, and must only be invoked by the governance gateway after approval and safety checks.

### Safety provider

```python
class SafetyCheckRequest(BaseModel):
    text: str
    context: str
    metadata: dict = {}

class SafetyCheckResult(BaseModel):
    passed: bool
    severity: str
    categories: list[str]
    explanation: str
    raw: dict = {}

class SafetyProvider(ABC):
    @abstractmethod
    async def check_input(self, request: SafetyCheckRequest) -> SafetyCheckResult:
        pass

    @abstractmethod
    async def check_output(self, request: SafetyCheckRequest) -> SafetyCheckResult:
        pass
```

### Audit logger

```python
class AuditEventCreate(BaseModel):
    actor_user_id: str | None
    company_id: str
    action: str
    entity_type: str
    entity_id: str
    before_state: dict | None = None
    after_state: dict | None = None
    metadata: dict = {}

class AuditLogger(ABC):
    @abstractmethod
    async def record(self, event: AuditEventCreate) -> None:
        pass
```

## Required seed scenario

Create fictional company:

```text
Acme Corp
```

Create systems:

| System | Department | Risk | Status | Narrative purpose |
|---|---:|---:|---:|---|
| Customer Support Summariser | Customer Success | Medium | Approved | Main governed model call demo. |
| Sales Email Generator | Sales | Low | Approved | Low-risk contrast case. |
| HR CV Screening Assistant | HR | High | Pending or Blocked | Shows why governance blocks some uses. |
| Finance Report Assistant | Finance | Medium | Approved | Cost/reporting demo. |
| Marketing Content Assistant | Marketing | Medium | Approved | Prompt injection/policy demo. |

Create synthetic data:

- Model runs for 30 days.
- Several failed evaluations.
- At least one PII exposure incident.
- At least one hallucination incident.
- At least one jailbreak/policy violation attempt.
- Multiple human review statuses.
- Audit events for approvals, prompt edits, review decisions.

## Coding standards

### Backend

- Use service classes for business logic; keep route handlers thin.
- Use Pydantic schemas at API boundaries.
- Use SQLAlchemy models only inside persistence layer.
- Use Alembic for every schema change.
- Use dependency injection for DB sessions and providers.
- Use structured errors with stable error codes.
- Do not log full prompts/outputs to console by default.
- Write tests for risk routing and review decisions.

### Frontend

- Type all API responses.
- Use server components where appropriate, client components for interactive charts/tables.
- Do not call LLM providers from the browser.
- Keep design tokens centralised.
- Every table needs loading, empty, and error states.
- Every status/risk colour must also have text or icon semantics.
- Avoid overusing animations; governance should feel calm and controlled.

## GitHub Actions baseline

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e backend[dev]
      - run: ruff check backend
      - run: pytest backend/tests

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 'lts/*'
      - run: cd frontend && corepack enable && pnpm install --frozen-lockfile
      - run: cd frontend && pnpm lint
      - run: cd frontend && pnpm test
      - run: cd frontend && pnpm build
```

## Definition of done for MVP

The MVP is done when:

- A developer can run the full app locally using documented steps.
- The dashboard has the command-centre visual identity from `DESIGN.md`.
- The registry, system detail, governance gateway, review queue, incidents, and audit pages work with seeded data.
- At least one live or mocked LLM run can flow through all governance checks.
- PII/hallucination/policy failures can be demonstrated.
- Review decisions and incidents are auditable.
- The codebase has tests for core routing logic.
- Azure integration points are documented and at least one adapter stub exists.
