# Specification

What the Acme Operations Agentic Assistant must do. Governed by [constitution.md](constitution.md).

## 1. Problem

Acme Operations is a mid-sized enterprise improving the efficiency of its customer support and account management. Internal users (sales, support, operations staff) ask operational questions that today require navigating multiple systems by hand. We replace that with one secure, auditable agent interface.

Canonical query:

> "Show me open customer issues for Client X, summarise the latest status, and suggest the next action."

## 2. Users and roles

Three roles, sourced from Keycloak token claims, enforced server-side. These are the brief's required roles; the prototype is scoped to the customer-support domain (account management is deferred, see [ADR-0008](adr/0008-scope-support-domain-only.md)). See [ADR-0004](adr/0004-keycloak-rbac.md) and the full rules in [rbac-matrix.md](rbac-matrix.md).

| Role | Can read | Can write |
|------|----------|-----------|
| `sales_user` | Customers and issues (read-only) | Nothing |
| `support_user` | Customers and issues | Update issues, add issue updates |
| `admin` | Everything | Update issues, create next actions, manage users |

## 3. Functional requirements

### FR-1 Authentication
- FR-1.1 Users authenticate via Keycloak OIDC, or present a valid bearer token, before any query.
- FR-1.2 The API validates the bearer token on every request.
- FR-1.3 Expired or invalid tokens return `401`. Token validation rules (issuer, audience, signature, expiry) are specified in [security-spec.md](security-spec.md).

### FR-2 Query processing
- FR-2.1 A user submits a natural-language query through the UI (FR-9) or the API.
- FR-2.2 The agent (LLM via Ollama) decides dynamically which tools to call. Prompt-only answers that bypass tools do not satisfy this.
- FR-2.3 The agent may call tools in sequence, feeding results back into reasoning.
- FR-2.4 The agent returns a grounded natural-language answer plus structured citations of the data used.
- FR-2.5 The agent loop is bounded and constrained per [agent-spec.md](agent-spec.md): a maximum step count, declared tools only, and no ability to widen its own data scope.

### FR-3 Data retrieval and updates
- FR-3.1 Structured data lives in PostgreSQL: `customers`, `issues`, `issue_updates`, `next_actions`, `users`. See [data-spec.md](data-spec.md).
- FR-3.2 The agent reads and writes data only through MCP tools, never raw SQL from the model.
- FR-3.3 Reads and writes run scoped to the caller's role (least privilege).
- FR-3.4 Writes (issue updates, next actions) are permitted only for roles authorised in [rbac-matrix.md](rbac-matrix.md). See [ADR-0007](adr/0007-read-write-operations.md).

### FR-4 Tools (MCP)
- FR-4.1 Tools are declared with input and output JSON schemas. See [tools.md](tools.md).
- FR-4.2 Initial tool set:
  - `get_customer` — retrieve a customer profile by name.
  - `list_open_issues` — retrieve open issues for a customer.
  - `get_issue` — retrieve one issue.
  - `summarise_issue_history` — summarise the history of a specific issue from its updates.
  - `update_issue` — update an issue (status) and add an update, for `support_user`/`admin`.
  - `create_next_action` — create a recommended next action for an issue, for `admin`.
- FR-4.3 Every tool call is validated, authorised, and traced.

### FR-5 Skill engine
- FR-5.1 A skill is a reusable, named multi-step procedure built on tools. The first skill is **Customer Escalation Summary** ([skills/customer-escalation-summary.md](skills/customer-escalation-summary.md)).
- FR-5.2 Skills are declarative and discoverable by the agent, and clearly distinct from a one-off prompt call.
- FR-5.3 Skills respect the same RBAC as direct tool calls.

### FR-6 Session memory
- FR-6.1 Conversation context persists per user session in Redis.
- FR-6.2 Sessions expire after a configurable TTL.
- FR-6.3 Memory never crosses users or sessions.

### FR-7 Observability
- FR-7.1 Every request emits a trace: spans for agent steps, tool calls, and data queries. See [observability-spec.md](observability-spec.md).
- FR-7.2 Logs and traces include caller identity, role, tool inputs and outputs.
- FR-7.3 Errors and latency are captured per span.

### FR-8 Evaluation
- FR-8.1 An evaluation set of 5–10 questions scores: correct tool selection, groundedness in database results, RBAC compliance, and reasonableness of recommended next actions. RBAC and groundedness are hard release gates (100%); tool selection and next-action reasonableness are tracked targets. See [eval-spec.md](eval-spec.md).
- FR-8.2 Evaluations run on demand and in CI.
- FR-8.3 A run produces a scored report.

### FR-9 Minimal UI
- FR-9.1 A minimal web chat UI lets a user log in via Keycloak, submit a query, and read the grounded answer with its citations.
- FR-9.2 The UI calls only the public API (`/v1/query`, `/v1/sessions`); it holds no business logic and enforces no authorisation (constitution II). It attaches the Keycloak bearer token to every request.
- FR-9.3 The UI runs locally as part of `docker compose up`, served by the application service.

## 4. Non-functional requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Local-only core, open-source licences, runs via `docker compose up` | No proprietary core dependency |
| NFR-2 | Auth on every non-health endpoint | 100% of routes |
| NFR-3 | RBAC enforced server-side | 0 client-side authorisation checks |
| NFR-4 | Response latency (usability ceiling for a chat UI) | Provisional p95 ≤ 15 s on reference hardware [EVIDENCE NEEDED: confirm once hardware fixed] |
| NFR-5 | Trace coverage | 100% of requests traced |
| NFR-6 | Grounded answers | 0 fabricated operational facts in eval set |
| NFR-7 | Business outcome: time to answer an operational question vs the multi-system baseline | [EVIDENCE NEEDED: baseline minutes across current systems; target reduction] |

## 5. Out of scope (initial)

- External customer-facing access.
- Multi-language support.
- Fine-tuning of the base model.
- Write operations beyond issue updates and next actions (e.g. creating or deleting customers).

## 6. Acceptance criteria

- A `support_user` can log in through the UI, ask the canonical query, and receive a grounded answer with citations.
- A `sales_user` attempting to update an issue or create a next action receives a permission-scoped refusal, never the write.
- An `admin` can create a recommended next action for an issue, persisted to `next_actions`.
- The full request appears as a trace, with tool call logs, latency, and errors.
- The evaluation set produces a scored report covering tool selection, groundedness, RBAC, and next-action reasonableness.
