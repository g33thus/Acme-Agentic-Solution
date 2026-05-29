# Observability Spec

The required traces, spans, and attributes for every request. Governed by [constitution.md](constitution.md) (IV). Implements [spec.md](spec.md) FR-7 and [ADR-0006](adr/0006-phoenix-observability.md). Feeds build tasks T-7.1 to T-7.3.

Every action is auditable (constitution IV): who asked, what tools ran, what data was read, what the model returned. Traces use OpenTelemetry and export to Arize Phoenix. Target: **100% of requests traced** ([spec.md](spec.md) NFR-5).

## 1. Span hierarchy

One root span per request, nested by causality:

```
request                  (root, one per POST /v1/query)
└─ agent.step            (one per reasoning/tool-selection turn)
   └─ tool.call          (one per MCP tool invocation)
      └─ data.query      (one per PostgreSQL query the tool runs)
```

Skills ([skills/customer-escalation-summary.md](skills/customer-escalation-summary.md)) appear as a `skill.run` span between `agent.step` and the `tool.call` spans it composes.

## 2. Span names

| Span | Name | Emitted by |
|------|------|------------|
| root | `request` | FastAPI layer |
| agent turn | `agent.step` | agent loop |
| skill | `skill.run` | skill engine |
| tool | `tool.call:<tool_name>` | MCP server |
| data | `data.query:<entity>` | tool data layer |

## 3. Required attributes

Per [spec.md](spec.md) FR-7.2/7.3 and constitution IV. Missing a required attribute is a defect.

### Root `request`
| Attribute | Notes |
|-----------|-------|
| `trace_id` | Phoenix root trace id; returned to the client as `QueryResponse.traceId` (see §5) |
| `user.id` | authenticated subject from the Keycloak token |
| `user.role` | role used for authorisation ([rbac-matrix.md](rbac-matrix.md)) |
| `session.id` | Redis session id, if any |
| `http.status_code` | final response status |
| `latency_ms` | total request duration |
| `error` | set on failure with type and message |

### `tool.call:<tool_name>`
| Attribute | Notes |
|-----------|-------|
| `tool.name` | one of the [tools.md](tools.md) tools |
| `tool.input` | validated arguments |
| `tool.output` | validated result (size or content per retention policy) |
| `tool.authorised` | boolean; false denials recorded, never silently dropped |
| `latency_ms` | tool duration |
| `error` | on validation or authorisation failure |

### `data.query:<entity>`
| Attribute | Notes |
|-----------|-------|
| `db.entity` | `customers`/`issues`/`issue_updates`/`next_actions`/`users` |
| `db.operation` | `read` or `write` |
| `db.role_check` | the role authorisation applied (proves data-layer enforcement, constitution VI) |
| `db.rows_returned` / `db.rows_written` | row count |
| `latency_ms` | query duration |

Writes (`update_issue`, `create_next_action`) record the authoring user for audit (constitution IV), matching `issue_updates.author_id` / `next_actions.created_by` in [data-spec.md](data-spec.md).

**Trace data protection.** Raw tokens and passwords are never traced; large tool outputs may be truncated or size-recorded. See [security-spec.md](security-spec.md) §3 for retention and access rules.

## 4. Errors and latency

Every span records `latency_ms`. Failures set `error` with type and message and mark the span status as error; the root span propagates the final `http.status_code`. No request completes without a closed root span (NFR-5).

## 5. Trace id contract

The `traceId` returned in `QueryResponse` ([api/openapi.yaml](api/openapi.yaml)) **equals** the `trace_id` of the root `request` span in Phoenix. This is the audit handle: given a response, an auditor finds the exact trace. The eval harness asserts this linkage for every case ([eval-spec.md](eval-spec.md) §5).
