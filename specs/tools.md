# Tool Contract (MCP)

The declared MCP tools the agent may call. Governed by [constitution.md](constitution.md) (III, V). Implements [spec.md](spec.md) FR-4 and [ADR-0003](adr/0003-mcp-for-tools.md). Feeds build task T-4.2.

## Why MCP here

The agent acts **only** through these declared tools (constitution V); the model never issues raw SQL ([spec.md](spec.md) FR-3.2). MCP separates *tool definitions* (name, input/output schema, authorisation) from *agent logic* (planning and reasoning). Benefits in this context:

- The agent's reasoning is decoupled from data access. Tools can change implementation without touching the agent.
- Each tool is independently validated, authorised, and traced ([observability-spec.md](observability-spec.md)).
- The tool surface is the security boundary: RBAC ([rbac-matrix.md](rbac-matrix.md)) is enforced per tool, not in prompts.

## Shared rules

Apply to every tool (FR-4.3):

1. **Validate** input against the input schema.
2. **Authorise** against [rbac-matrix.md](rbac-matrix.md) using the caller's role from request context. Reads and writes have different rules.
3. **Scope** the read or write in the data layer; never retrieve then filter ([data-spec.md](data-spec.md)).
4. **Validate** output against the output schema.
5. **Trace** the call: tool name, arguments, result, latency, errors.
6. **Groundable**: every returned fact is stored data, so the agent can cite it (constitution III). Each tool states the `Citation.source` it backs, matching `Citation` in [api/openapi.yaml](api/openapi.yaml).

Common error shape on authorisation or validation failure: `{ "error": string, "detail"?: string }`, consistent with the API `Error` schema. A write denied by RBAC returns this with no side effect.

## Read tools

### `get_customer`
Purpose: retrieve a customer profile by name. Citation source: `customers`. RBAC: all roles (read).

Input:
```json
{
  "type": "object",
  "required": ["name"],
  "properties": { "name": { "type": "string", "minLength": 1 } },
  "additionalProperties": false
}
```
Output:
```json
{
  "type": "object",
  "required": ["id", "name"],
  "properties": {
    "id": { "type": "string" },
    "name": { "type": "string" },
    "tier": { "type": ["string", "null"] },
    "region": { "type": ["string", "null"] },
    "openIssueCount": { "type": "integer" }
  },
  "additionalProperties": false
}
```

### `list_open_issues`
Purpose: retrieve all open issues for a customer. Citation source: `issues`. RBAC: all roles (read).

Input:
```json
{
  "type": "object",
  "required": ["customerId"],
  "properties": { "customerId": { "type": "string" } },
  "additionalProperties": false
}
```
Output:
```json
{
  "type": "object",
  "required": ["issues"],
  "properties": {
    "issues": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "customerId", "title", "status", "priority"],
        "properties": {
          "id": { "type": "string" },
          "customerId": { "type": "string" },
          "title": { "type": "string" },
          "status": { "type": "string", "enum": ["open", "in_progress", "resolved", "closed"] },
          "priority": { "type": "string", "enum": ["low", "medium", "high", "critical"] },
          "updatedAt": { "type": "string", "format": "date-time" }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

### `get_issue`
Purpose: retrieve one issue. Citation source: `issues`. RBAC: all roles (read).

Input:
```json
{
  "type": "object",
  "required": ["id"],
  "properties": { "id": { "type": "string" } },
  "additionalProperties": false
}
```
Output: a single object with the same shape as a `list_open_issues.issues[]` item, plus optional `customerId` and full status set.

### `summarise_issue_history`
Purpose: summarise the history of a specific issue from its `issue_updates`. Citation source: `issue_updates` (the update rows summarised) and `issues` (the issue id). RBAC: all roles (read).

Input:
```json
{
  "type": "object",
  "required": ["issueId"],
  "properties": { "issueId": { "type": "string" } },
  "additionalProperties": false
}
```
Output:
```json
{
  "type": "object",
  "required": ["issueId", "summary", "updateIds"],
  "properties": {
    "issueId": { "type": "string" },
    "summary": { "type": "string", "description": "grounded in the named updates only" },
    "updateIds": { "type": "array", "items": { "type": "integer" } }
  },
  "additionalProperties": false
}
```

## Write tools

### `update_issue`
Purpose: update an issue's status and add an issue update note. Citation source: `issues`. RBAC: `support_user`, `admin` only ([rbac-matrix.md](rbac-matrix.md)). Records `issue_updates.author_id` for audit.

Input:
```json
{
  "type": "object",
  "required": ["id"],
  "properties": {
    "id": { "type": "string" },
    "status": { "type": "string", "enum": ["open", "in_progress", "resolved", "closed"] },
    "note": { "type": "string", "description": "added to issue_updates" }
  },
  "additionalProperties": false
}
```
Output:
```json
{
  "type": "object",
  "required": ["id", "status", "updatedAt"],
  "properties": {
    "id": { "type": "string" },
    "status": { "type": "string", "enum": ["open", "in_progress", "resolved", "closed"] },
    "updateId": { "type": ["integer", "null"], "description": "id of the added issue_update, if any" },
    "updatedAt": { "type": "string", "format": "date-time" }
  },
  "additionalProperties": false
}
```

### `create_next_action`
Purpose: create a recommended next action for an issue, grounded in its current status and history. Citation source: `next_actions` (the new row) and `issues`. RBAC: `admin` only ([rbac-matrix.md](rbac-matrix.md)). Records `next_actions.created_by`.

Input:
```json
{
  "type": "object",
  "required": ["issueId", "action"],
  "properties": {
    "issueId": { "type": "string" },
    "action": { "type": "string" },
    "rationale": { "type": "string", "description": "grounded justification" }
  },
  "additionalProperties": false
}
```
Output:
```json
{
  "type": "object",
  "required": ["id", "issueId", "action", "status"],
  "properties": {
    "id": { "type": "integer" },
    "issueId": { "type": "string" },
    "action": { "type": "string" },
    "rationale": { "type": ["string", "null"] },
    "status": { "type": "string", "enum": ["proposed", "accepted", "done", "rejected"] }
  },
  "additionalProperties": false
}
```

## Citation sources

| Tool | `Citation.source` | `Citation.ref` |
|------|-------------------|----------------|
| `get_customer` | `customers` | customer id |
| `list_open_issues`, `get_issue`, `update_issue` | `issues` | issue id |
| `summarise_issue_history` | `issue_updates` | update id (issue id for context) |
| `create_next_action` | `next_actions` | next-action id |
