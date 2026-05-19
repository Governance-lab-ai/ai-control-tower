# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-12  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


## Environment strategy

The project should support three environment modes:

| Mode | Purpose | External dependencies |
|---|---|---|
| `local` | Developer/demo mode. | Local Postgres, mock providers. |
| `azure-dev` | Optional Azure integration testing. | Azure OpenAI/Content Safety/etc. if configured. |
| `production` | Future hardened deployment. | Azure services, Entra, Key Vault, Monitor. |

## Configuration rules

- Keep config in environment variables.
- Provide `.env.example` files with placeholders only.
- Never commit real secrets.
- Frontend should only receive safe public config.
- Backend owns provider credentials.
- Azure secrets should move to Key Vault in deployed environments.

## Root `.env.example`

```text
APP_ENV=local
COMPANY_SEED_NAME=Acme Corp
```

## Backend `.env.example`

```text
APP_ENV=local
APP_NAME=AI Governance Control Tower
API_V1_PREFIX=/api/v1

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/aigov

AUTH_MODE=local_mock
LOCAL_DEFAULT_USER_EMAIL=admin@example.test
LOCAL_DEFAULT_USER_ROLE=governance_admin

LLM_PROVIDER=mock
SAFETY_PROVIDER=local
SECRET_PROVIDER=env
TELEMETRY_PROVIDER=console
DATA_GOVERNANCE_PROVIDER=local

# Optional direct provider keys for local experiments only
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Azure optional
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT_NAME=
AZURE_OPENAI_API_VERSION=

AZURE_CONTENT_SAFETY_ENDPOINT=
AZURE_CONTENT_SAFETY_KEY=

AZURE_KEY_VAULT_URL=
APPLICATIONINSIGHTS_CONNECTION_STRING=
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=

# Limits
MAX_INPUT_CHARS=12000
MAX_OUTPUT_CHARS=12000
MAX_RETRIEVED_DOCUMENTS=5
REQUEST_TIMEOUT_SECONDS=30
RATE_LIMIT_PER_MINUTE=60
```

## Frontend `.env.example`

```text
NEXT_PUBLIC_APP_ENV=local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_MODE=local_mock
NEXT_PRIVATE_API_BASE_URL=http://localhost:8000
```

Do not add:

```text
NEXT_PUBLIC_OPENAI_API_KEY
NEXT_PUBLIC_AZURE_OPENAI_API_KEY
NEXT_PUBLIC_CONTENT_SAFETY_KEY
```

No provider secrets should be public.

Episode 1 implements these templates at:

- `.env.example`
- `backend/.env.example`
- `frontend/.env.example`

## Docker Compose environment

Minimal local services:

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: aigov
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Provider selection

Use environment variables to switch providers:

```text
LLM_PROVIDER=mock | openai | anthropic | azure_openai
SAFETY_PROVIDER=local | azure_content_safety
SECRET_PROVIDER=env | azure_key_vault
TELEMETRY_PROVIDER=console | azure_monitor
AUTH_MODE=local_mock | entra
```

Provider factory example:

```python
def get_llm_provider(settings: Settings) -> LLMProvider:
    if settings.LLM_PROVIDER == "mock":
        return MockLLMProvider()
    if settings.LLM_PROVIDER == "azure_openai":
        return AzureOpenAIProvider(settings)
    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
```

## Local mock user model

For local mode, support a simple mock identity.

Suggested dev headers:

```text
X-Demo-User-Email: admin@example.test
X-Demo-User-Role: governance_admin
```

Only enable this in `APP_ENV=local`.

## Environment safety checks

On app startup:

- If `APP_ENV=production`, reject `AUTH_MODE=local_mock`.
- If `APP_ENV=production`, reject `SECRET_PROVIDER=env` unless explicitly allowed.
- If Azure provider selected, require endpoint and credentials/managed identity.
- If frontend receives secret-like variables, fail build or warn loudly.
- If database URL points to localhost in production, fail startup.

## Secret rotation readiness

Provider clients should not assume secrets never change.

Later improvements:

- Refresh Key Vault secrets periodically.
- Support managed identity.
- Use short-lived credentials where possible.
- Emit audit event when integration config changes.
