# ADR-0001: Local, open-source stack

- Status: Accepted
- Date: 2026-05-29

## Context

Acme Operations handles internal customer and account data. The assistant must keep that data inside Acme's environment and avoid licence lock-in or per-token SaaS costs.

## Decision

Build the core on local, open-source components only: Ollama (LLM), FastAPI, PostgreSQL, Redis, Keycloak, Arize Phoenix, MCP. No proprietary SaaS in the core request path. Orchestrate locally with docker-compose.

## Consequences

Positive:
- Data stays local; lower exposure and no per-token cost.
- Full control over versions and configuration.
- Reproducible local setup.

Negative:
- Local model quality and latency depend on hardware.
- Operational burden of running the stack falls on Acme.

## Rejected alternatives

- Hosted LLM API: rejected for data residency and recurring cost.
- Proprietary observability SaaS: rejected for licence cost and data egress.
