# Security Spec

The security controls the system must implement. Governed by [constitution.md](constitution.md) (II, IV, VI). Implements [spec.md](spec.md) FR-1, FR-3.3, FR-7. Feeds build tasks in Phase 2 (auth), Phase 4 (tool authorisation), and Phase 7 (observability).

Security is server-side and layered: authenticate the caller, authorise every action against the server-side role, treat all model input as untrusted, and keep sensitive data out of traces.

## 1. Token validation

Every non-health request carries a Keycloak-issued OIDC bearer token ([ADR-0004](adr/0004-keycloak-rbac.md)). The API validates, on every request, before any agent or tool runs:

| Check | Rule |
|-------|------|
| Signature | Verified against Keycloak's JWKS; keys cached and refreshed on rotation |
| Algorithm | Allowlist (e.g. `RS256`); `none` and symmetric algs rejected |
| Issuer (`iss`) | Equals the configured Keycloak realm issuer |
| Audience (`aud`) | Contains the configured API client id |
| Expiry (`exp`)/not-before (`nbf`) | Current time within bounds, with small allowed clock skew |
| Role claim | Mapped to exactly one of `sales_user`, `support_user`, `admin` |

Any failure returns `401` ([api/openapi.yaml](api/openapi.yaml), FR-1.3). The application never stores passwords (constitution II). The validated subject and role become the **request context** that the tool layer authorises against; nothing downstream can alter them.

## 2. Prompt injection and untrusted content

An agentic system over RBAC data must assume both the user query and the retrieved data may try to manipulate the agent.

- **RBAC is authoritative server-side.** No text in the query, conversation memory, or tool output can change the caller's role or grant a write the role lacks. The tool layer authorises against the request-context role on every call ([rbac-matrix.md](rbac-matrix.md), [agent-spec.md](agent-spec.md) §4). This makes injection unable to cross the data boundary even if it manipulates the model's wording.
- **Retrieved data is content, not instructions.** The system prompt instructs the agent to treat tool results as data ([agent-spec.md](agent-spec.md) §5). Stored notes (e.g. an `issue_update` containing "ignore your instructions") are never executed as commands.
- **Tool inputs are schema-validated** ([tools.md](tools.md)); the model cannot smuggle extra fields or operations.
- **No raw SQL / code path exists** (constitution V), so injection cannot reach the database directly.
- Residual risk is limited to wording/social-engineering of the natural-language answer within already-authorised data; this is covered by the groundedness and RBAC eval gates ([eval-spec.md](eval-spec.md)).

## 3. Trace and log data protection

Traces capture tool inputs and outputs ([observability-spec.md](observability-spec.md)), which include customer data and identity. Controls:

| Concern | Control |
|---------|---------|
| Credentials | No passwords or raw bearer tokens are ever logged or traced |
| Identity | `user.id` and `user.role` are recorded for audit (constitution IV) |
| Large payloads | Tool output may be truncated or size-recorded per a retention policy rather than stored whole |
| Access | Phoenix and trace stores are local ([ADR-0006](adr/0006-phoenix-observability.md)); access is restricted to authorised operators |
| Retention | Traces retained for the audit window then purged; retention period is configurable |

The audit requirement (constitution IV) is met by the durable write attribution in the data layer (`issue_updates.author_id`, `next_actions.created_by`, [data-spec.md](data-spec.md)) plus traces; traces alone are not the system of record.

## 4. Session isolation

Conversation memory lives in Redis ([ADR-0005](adr/0005-postgres-redis-storage.md)), per [spec.md](spec.md) FR-6.

- Session keys are namespaced by the authenticated subject; one user's session can never be read under another identity (FR-6.3).
- A session is bound to the identity that created it; presenting a different token does not load it.
- Sessions expire on a configurable TTL (FR-6.2). Memory is ephemeral and never the source of truth ([data-spec.md](data-spec.md) §3).

## 5. Secrets

- All secrets (Keycloak client secret, DB credentials, Redis auth) come from environment or a secrets store, never source control (constitution II).
- `.env.example` documents required variables with no real values (build task T-0.3).

## 6. Transport and surface

- Only `/health` is unauthenticated ([api/openapi.yaml](api/openapi.yaml)); every other route requires a valid token (NFR-2).
- The UI ([spec.md](spec.md) FR-9) holds no authorisation logic and only forwards the bearer token; it is not a trust boundary (constitution II).
- Local deployment runs over the compose network; exposing the API beyond localhost requires TLS termination, out of scope for the initial prototype ([spec.md](spec.md) §5).
