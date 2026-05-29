# Constitution

Non-negotiable principles for the Acme Operations Agentic Assistant. Every spec, plan, and line of code must respect these.

## I. Local and open-source first

All core components run locally and use open-source licences. No proprietary SaaS dependency in the core path. LLM inference runs through Ollama on local hardware. See [ADR-0001](adr/0001-local-open-source-stack.md).

## II. Security by default

- No endpoint is public without authentication, except health checks.
- Authentication is delegated to Keycloak (OIDC). The application never stores passwords.
- Authorisation is role-based (RBAC) and enforced server-side on every tool call and data query, never in the client.
- Secrets come from environment or a secrets store, never source control.

## III. Grounded answers only

The agent answers from retrieved, structured data. It must not fabricate operational facts. Every factual claim in a response traces to a tool result. Unverifiable requests return an explicit "no data" answer.

## IV. Every action is auditable

Each request produces a trace: who asked, what tools ran, what data was read, what the model returned. Traces are observable in Arize Phoenix and retained for audit. See [ADR-0006](adr/0006-phoenix-observability.md).

## V. Tools over free-form code

The agent acts only through declared tools exposed by the MCP server. No arbitrary code execution. Tool inputs and outputs are schema-validated. See [ADR-0003](adr/0003-mcp-for-tools.md).

## VI. Least privilege data access

Data queries run under the caller's role. A user sees only what their role permits. Row and column scope is enforced in the data layer, not filtered after retrieval.

## VII. Evaluable before shippable

No agent behaviour ships without an evaluation. Quality, groundedness, and RBAC enforcement are measured against a test set before release.

## VIII. Specs are the source of truth

Behaviour, architecture, and API changes update the matching spec in the same change. Code that contradicts a spec is a defect in one of them.

## Amendment

Changing a principle requires a new ADR recording the reason and the rejected alternative.
