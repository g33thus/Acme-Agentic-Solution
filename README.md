# Acme Operations Agentic Assistant

A secure, auditable agent that answers internal operational questions ("show me open issues for Client X, summarise the latest status, and suggest the next action") over Acme's customer support and account-management data. Runs entirely locally.

Specs are the source of truth. See [specs/](specs/) and start at [specs/README.md](specs/README.md).

## Stack

| Concern | Choice |
|---------|--------|
| API + UI | Python 3.12, FastAPI, Uvicorn |
| LLM | Ollama (local open model) |
| Tools | MCP (Model Context Protocol) |
| Auth + RBAC | Keycloak (OIDC) |
| Data | PostgreSQL |
| Session memory | Redis |
| Observability + eval | Arize Phoenix, OpenTelemetry |
| Orchestration | Docker Compose |

## Run locally

```bash
cp .env.example .env
docker compose up
```

Then:
- API health: http://localhost:8000/health
- Keycloak: http://localhost:8080
- Phoenix (traces): http://localhost:6006


