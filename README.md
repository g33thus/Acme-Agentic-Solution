# Acme Operations Agentic Assistant

A secure, auditable agent that answers internal operational questions ("show me open issues for Client X, summarise the latest status, and suggest the next action") over Acme's customer-support data. Runs entirely locally. Scope is held to the brief's customer-support domain; account management is deferred ([specs/adr/0008-scope-support-domain-only.md](specs/adr/0008-scope-support-domain-only.md)).

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

Build status: **Phase 0 (foundations) complete.** Data, auth, API, MCP tools, agent, skills, observability, and eval are built in later phases. See [specs/tasks.md](specs/tasks.md).

## Why MCP

MCP separates **tool definitions** (name, input/output schema, authorisation) from **agent logic** (planning and reasoning). The agent acts only through declared tools, never raw SQL. Benefits here:

- Data access is decoupled from reasoning; tools change without touching the agent.
- Each tool is independently validated, authorised, and traced.
- The tool surface is the security boundary: RBAC is enforced per tool, not in prompts.

Tool contracts: [specs/tools.md](specs/tools.md).

## Redis versus PostgreSQL

- **PostgreSQL** holds the durable system of record (customers, issues, issue_updates, next_actions, users): relational integrity, audited writes, survives restart. Answers must be grounded in it.
- **Redis** holds ephemeral per-session conversation memory and recent tool-call results with a TTL: fast, expendable, scoped to one session, never the source of truth.

Rule: durable, relational, or audited → PostgreSQL. Per-session, latency-sensitive, safe to lose → Redis. Detail in [specs/data-spec.md](specs/data-spec.md).

## Roles (RBAC)

| Role | Access |
|------|--------|
| `sales_user` | Read-only customer and issue data |
| `support_user` | Read and update issues, add issue updates |
| `admin` | Full access, including creating next actions and managing users |

Enforced server-side in the tool layer, by operation (read vs write). Matrix: [specs/rbac-matrix.md](specs/rbac-matrix.md). Scope rationale: [specs/adr/0008-scope-support-domain-only.md](specs/adr/0008-scope-support-domain-only.md).

## AI tool usage

This project was built with AI coding assistance (Claude Code). Full notes — what was delegated, how output was validated, errors caught, and what was kept under human control — are in [AI-USAGE.md](AI-USAGE.md). In brief: AI drafted the specs, schema, and scaffolding from the brief; a human owns scope decisions (e.g. trimming to the support domain), reviews every diff, and validates RBAC, groundedness, and security claims against the specs before they count as done.
