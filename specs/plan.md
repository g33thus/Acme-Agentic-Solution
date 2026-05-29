# Technical Plan

How we build the system in [spec.md](spec.md). Governed by [constitution.md](constitution.md).

## 1. High-level architecture

```
                         ┌──────────────┐
                         │   Keycloak   │  OIDC auth, roles
                         └──────┬───────┘
                                │ validate token
   User ──HTTP──▶ ┌────────────▼─────────────┐
                  │   FastAPI API layer       │  routes, authz, session
                  └─────┬───────────────┬─────┘
                        │               │
              session   │               │ invoke
                 ▼       │               ▼
            ┌────────┐   │       ┌───────────────┐
            │ Redis  │   │       │     Agent      │  LLM reasoning
            │ memory │   │       │  (Ollama LLM)  │
            └────────┘   │       └───────┬───────┘
                         │               │ tool calls
                         │               ▼
                         │       ┌───────────────┐
                         │       │  MCP server   │  declared tools
                         │       │ + Skill engine│
                         │       └───────┬───────┘
                         │               │ scoped queries
                         │               ▼
                         │       ┌───────────────┐
                         │       │  PostgreSQL   │  structured data
                         │       └───────────────┘
                         │
                         ▼
                  ┌───────────────┐
                  │ Arize Phoenix │  traces, evals
                  └───────────────┘
```

## 2. Components

### 2.1 FastAPI API layer
- Entry point for all requests.
- Validates Keycloak bearer token, extracts identity and roles.
- Manages session lifecycle (Redis).
- Delegates query to the agent.
- Emits the root trace span.
- Contract defined in [api/openapi.yaml](api/openapi.yaml).

### 2.2 Agent (Ollama)
- Runs an open-source model locally through Ollama. See [ADR-0002](adr/0002-ollama-llm-runtime.md).
- Receives the user query plus session context.
- Plans and calls MCP tools, loops on results, produces grounded answer with citations.
- Constrained to act only via declared tools. See [ADR-0003](adr/0003-mcp-for-tools.md).
- Loop is bounded (max steps, no repeat-calls, deadline) and cannot widen its own data scope. See [agent-spec.md](agent-spec.md).

### 2.3 MCP server
- Exposes tools with JSON input and output schemas. See [tools.md](tools.md).
- Each tool: validate input, check authorisation for the caller role, run scoped read or write, return validated output, emit span.
- Tools listed in spec FR-4.2: `get_customer`, `list_open_issues`, `get_issue`, `summarise_issue_history`, `update_issue`, `create_next_action`.
- The tool surface is the security boundary: RBAC enforced here, never in prompts. See [security-spec.md](security-spec.md).

### 2.4 Skill engine
- Registers named multi-step procedures composed of tools.
- Discoverable by the agent as higher-level capabilities.
- Inherits RBAC from underlying tools.

### 2.5 PostgreSQL
- Stores customers, issues, issue_updates, next_actions, users. See [ADR-0005](adr/0005-postgres-redis-storage.md) and [data-spec.md](data-spec.md).
- Role scoping enforced through parameterised, role-scoped reads and writes in the tool layer.

### 2.6 Redis
- Per-session conversation memory with TTL. See [ADR-0005](adr/0005-postgres-redis-storage.md).
- Keyed by session id derived from authenticated identity.

### 2.7 Keycloak
- OIDC provider. Issues tokens with role claims. See [ADR-0004](adr/0004-keycloak-rbac.md).

### 2.8 Arize Phoenix
- Receives OpenTelemetry traces from API, agent, and tools.
- Hosts the evaluation harness and stores eval results. See [ADR-0006](adr/0006-phoenix-observability.md).

### 2.9 Minimal UI
- Lightweight web chat page: Keycloak login, query box, answer with citations. Implements spec FR-9.
- Thin client over the public API; no business logic, no authorisation. Attaches the bearer token to each call.
- Served by the application service (static assets), so no extra container is required.

## 3. Request flow

1. User sends query with bearer token to FastAPI.
2. API validates token against Keycloak, extracts role.
3. API loads or creates the Redis session, opens root trace span.
4. API passes query plus context to the agent.
5. Agent reasons, selects tools or a skill.
6. MCP server authorises each call against the role, runs the scoped read or write, returns data, emits spans.
7. Agent composes a grounded answer with citations.
8. API persists updated context to Redis, closes the trace, returns the response.

## 4. Proposed technology

| Concern | Choice | ADR |
|---------|--------|-----|
| Runtime | Python 3.12, FastAPI, Uvicorn | — |
| LLM | Ollama (local open model) | [0002](adr/0002-ollama-llm-runtime.md) |
| Tooling protocol | MCP | [0003](adr/0003-mcp-for-tools.md) |
| Auth | Keycloak OIDC | [0004](adr/0004-keycloak-rbac.md) |
| Data | PostgreSQL | [0005](adr/0005-postgres-redis-storage.md) |
| Session | Redis | [0005](adr/0005-postgres-redis-storage.md) |
| Observability and eval | Arize Phoenix, OpenTelemetry | [0006](adr/0006-phoenix-observability.md) |
| Local orchestration | docker-compose | — |

## 5. Repository layout (planned)

```
acme-agent/
  app/            FastAPI app, routes, auth, session
  ui/             minimal web chat UI, served by app
  agent/          agent loop, prompt, model client
  mcp_server/     tool definitions, schemas, authz
  skills/         skill definitions
  db/             schema, migrations, seed data
  eval/           evaluation harness and test set
  observability/  tracing setup
docker-compose.yml
specs/            this directory
```

## 6. Risks and open questions

- Local model capability for reliable tool selection. Mitigation: evaluation harness gates releases (RBAC + groundedness hard gates).
- Latency: provisional p95 ceiling of 15 s for chat usability (NFR-4); confirm on reference hardware. The agent deadline aligns to it ([agent-spec.md](agent-spec.md) §2).
- Write operations (issue updates, next actions) need careful authorisation. Mitigation: enforced in the tool layer per [rbac-matrix.md](rbac-matrix.md), recorded in [ADR-0007](adr/0007-read-write-operations.md).
- Prompt injection over RBAC data. Mitigation: server-side authorisation is authoritative and the agent cannot widen scope; retrieved data is treated as untrusted content. See [security-spec.md](security-spec.md) §2.
- Scope is deliberately limited to the customer-support domain for the prototype; account management is deferred. See [ADR-0008](adr/0008-scope-support-domain-only.md).
