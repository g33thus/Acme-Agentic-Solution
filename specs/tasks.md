# Build Tasks

Ordered, checkable tasks to implement [plan.md](plan.md). No code exists yet; this is the build sequence. Check items off as completed.

## Phase 0 — Foundations
- [ ] T-0.1 Create repository layout per plan section 5.
- [ ] T-0.2 Add `docker-compose.yml` for PostgreSQL, Redis, Keycloak, Phoenix, Ollama.
- [ ] T-0.3 Add `.env.example` and config loader (no secrets in source).
- [ ] T-0.4 Add `pyproject.toml`, lint, format, test tooling.

## Phase 1 — Data layer
- [ ] T-1.1 Define PostgreSQL schema: customers, issues, issue_updates, next_actions, users. See [data-spec.md](data-spec.md).
- [ ] T-1.2 Add migrations.
- [ ] T-1.3 Add seed data for local dev and the eval set, per the seed invariants in [data-spec.md](data-spec.md) (all three roles).
- [ ] T-1.4 Implement the RBAC matrix: read for all roles, write (issues/updates) for support_user/admin, next actions and user management for admin. Operation-based, server-side. See [rbac-matrix.md](rbac-matrix.md).

## Phase 2 — Auth
- [ ] T-2.1 Configure Keycloak realm, clients, and the three roles.
- [ ] T-2.2 FastAPI bearer-token validation middleware: JWKS signature, alg allowlist, issuer, audience, expiry/clock-skew. See [security-spec.md](security-spec.md) §1.
- [ ] T-2.3 Extract identity and role into immutable request context.
- [ ] T-2.4 Reject invalid/expired tokens with `401`.

## Phase 3 — API layer
- [ ] T-3.1 Implement routes from `api/openapi.yaml`.
- [ ] T-3.2 Health endpoint (unauthenticated).
- [ ] T-3.3 Query endpoint wired to the agent.
- [ ] T-3.4 Session create/load via Redis.
- [ ] T-3.5 Minimal web chat UI (Keycloak login, query box, answer with citations), served by the app. See spec FR-9.

## Phase 4 — MCP server and tools
- [ ] T-4.1 Stand up the MCP server.
- [ ] T-4.2 Implement tools from FR-4.2 with input/output schemas: `get_customer`, `list_open_issues`, `get_issue`, `summarise_issue_history`, `update_issue`, `create_next_action`. See [tools.md](tools.md).
- [ ] T-4.3 Enforce role authorisation (read vs write) in each tool, per [rbac-matrix.md](rbac-matrix.md).
- [ ] T-4.4 Validate every tool input and output.

## Phase 5 — Agent
- [ ] T-5.1 Ollama model client.
- [ ] T-5.2 Agent loop: plan, call tools, observe, repeat. Pin the model in config. See [agent-spec.md](agent-spec.md).
- [ ] T-5.3 Grounded answer composition with citations.
- [ ] T-5.4 Constrain agent to declared tools only.
- [ ] T-5.5 Enforce loop bounds (max steps, no repeat-calls, deadline) and the no-scope-widening property; treat retrieved data as untrusted. See [agent-spec.md](agent-spec.md) §2/§4, [security-spec.md](security-spec.md) §2.

## Phase 6 — Skill engine
- [ ] T-6.1 Skill registration and discovery.
- [ ] T-6.2 Implement first skill: "Customer Escalation Summary". See [skills/customer-escalation-summary.md](skills/customer-escalation-summary.md).
- [ ] T-6.3 Skills inherit tool RBAC.

## Phase 7 — Observability
- [ ] T-7.1 OpenTelemetry tracing across API, agent, tools.
- [ ] T-7.2 Export traces to Phoenix.
- [ ] T-7.3 Capture identity, role, tool I/O, latency, errors per span.
- [ ] T-7.4 Protect trace data: never log tokens/passwords, truncate large payloads, apply retention. See [security-spec.md](security-spec.md) §3.

## Phase 8 — Evaluation
- [ ] T-8.1 Build labelled test set of 5–10 questions. See [eval-spec.md](eval-spec.md), [eval/dataset.json](eval/dataset.json).
- [ ] T-8.2 Eval harness: tool selection, groundedness, RBAC compliance, next-action reasonableness. Enforce hard gates (RBAC + groundedness 100%) vs tracked targets (tool selection, next-action). See [eval-spec.md](eval-spec.md) §3.
- [ ] T-8.3 On-demand and CI runs producing a scored report.

## Phase 9 — Acceptance
- [ ] T-9.1 Verify spec section 6 acceptance criteria end-to-end.
- [ ] T-9.2 Confirm 100% trace coverage and 0 fabricated facts on the eval set.
