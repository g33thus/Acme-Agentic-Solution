# ADR-0007: Read-write operations for issues and next actions

- Status: Accepted
- Date: 2026-05-29
- Supersedes: the read-only stance previously stated in spec.md §5.

## Context

The client brief requires write capabilities the initial spec excluded:

- `support_user` must **update** issues and add issue updates.
- `admin` must **create and update** next actions.

The earlier spec declared all write operations out of scope ("read-only first"). That directly contradicts the brief, so the read-only decision is reversed for these specific operations.

## Decision

Permit a bounded set of writes, exposed only as MCP tools and authorised server-side per [rbac-matrix.md](../rbac-matrix.md):

- `update_issue` — set issue status and append an `issue_update`. Roles: `support_user`, `admin`.
- `create_next_action` — insert a `next_actions` row. Role: `admin`.

Writes follow the same path as reads (constitution V): validated input, role authorisation, parameterised statement in the tool layer, validated output, traced span. Every write records its author (`issue_updates.author_id`, `next_actions.created_by`) for audit (constitution IV).

## Consequences

Positive:
- Meets the client's support and admin workflows.
- Writes stay inside the tool and RBAC boundary; the model never issues SQL.
- Audit trail for every mutation.

Negative:
- Larger authorisation surface; write rules must be tested (covered by the eval set, [eval-spec.md](../eval-spec.md)).
- Data integrity and concurrency now matter for these tables.

## Scope boundary

Still out of scope (spec.md §5): creating or deleting customers, deleting issues, and any write not listed above. Widening this set requires a new ADR.

## Rejected alternatives

- Stay read-only: rejected; fails the client's hard requirements for `support_user` and `admin`.
- Allow arbitrary writes via a generic SQL tool: rejected; breaks constitution V (tools over free-form code) and the RBAC boundary.
