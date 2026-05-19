# Infrastructure

This folder is reserved for local orchestration notes and future Azure-aware infrastructure templates.

The local MVP is started from the repository root:

```bash
docker compose up --build
```

Current local services:

- `postgres`: local Postgres 16 database for application state.
- `backend`: FastAPI governance API at `http://localhost:8000`.
- `frontend`: Next.js dashboard at `http://localhost:3000`.

No real Azure resources are provisioned in Episode 1.
