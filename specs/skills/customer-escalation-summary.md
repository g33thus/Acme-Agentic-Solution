# Skill: Customer Escalation Summary

A reusable, named multi-step procedure built on tools. Governed by [constitution.md](constitution.md). Implements [spec.md](spec.md) FR-5 and the client's suggested skill. Feeds build task T-6.2.

A skill is declarative, discoverable by the agent, and clearly distinct from a one-off prompt call ([spec.md](spec.md) FR-5.2). It composes existing tools ([tools.md](tools.md)) and inherits their RBAC ([rbac-matrix.md](rbac-matrix.md)); it grants no access of its own (FR-5.3).

## Purpose

Given a customer, produce an executive escalation summary: the customer situation, a risk level, a recommended next action, and any missing information. This backs the canonical query and the support escalation workflow.

## Inputs

```json
{
  "type": "object",
  "required": ["customerName"],
  "properties": {
    "customerName": { "type": "string", "description": "customer to summarise, e.g. 'Client X'" }
  },
  "additionalProperties": false
}
```

Recent activity and open issues are gathered by the skill via tools; the caller supplies only the customer name.

## Steps

Ordered tool composition. Each step runs under the caller's role; empty scope yields a grounded "no data / no access" result, never fabrication (constitution III).

1. `get_customer` with `{ name: customerName }` → resolve the customer profile and id.
2. `list_open_issues` with `{ customerId }` → the open issues.
3. For each open issue (or the highest-priority ones): `summarise_issue_history` → latest grounded status.
4. Compose the outputs below. If the caller is `admin`, the recommended action may be persisted with `create_next_action`; otherwise it is proposed in the answer only ([rbac-matrix.md](rbac-matrix.md)).

## Outputs

The client requires these four. They map onto the API `QueryResponse` ([api/openapi.yaml](api/openapi.yaml)) `answer` plus `citations`.

```json
{
  "type": "object",
  "required": ["executiveSummary", "riskLevel", "recommendedNextAction", "missingInformation"],
  "properties": {
    "executiveSummary": { "type": "string", "description": "grounded summary of the customer situation" },
    "riskLevel": { "type": "string", "enum": ["Low", "Medium", "High", "Critical"] },
    "recommendedNextAction": { "type": "string" },
    "missingInformation": {
      "type": "array",
      "items": { "type": "string" },
      "description": "facts needed for a confident assessment but not present in the data"
    }
  },
  "additionalProperties": false
}
```

- `riskLevel` is derived from open-issue count, priority, and staleness of the latest update. The derivation must be grounded in retrieved data.
- `missingInformation` lists gaps (for example, no update in N days, no owner) so the summary never invents facts to fill them (constitution III).
- `citations`: one `Citation` per issue and update used.

## RBAC

Inherited from the composed tools. All roles can produce the read-only summary. Only `admin` may persist the recommended action via `create_next_action`; for other roles the action is advisory text. A user querying a customer they may not see gets a permission-scoped result.

## Worked example (seed data)

Caller `u-support` (role `support_user`), `customerName = "Client X"`:

1. `get_customer {name:"Client X"}` → `cust-x`, openIssueCount ≥ 1.
2. `list_open_issues {customerId:"cust-x"}` → `[issue-1001 (high), ...]`.
3. `summarise_issue_history {issueId:"issue-1001"}` → grounded latest status from its updates.
4. Output: executiveSummary citing `issue-1001`; `riskLevel: "High"` (open high-priority issue); recommendedNextAction; `missingInformation` if e.g. no recent update. Action is advisory (support_user cannot create next actions).

Same input as `u-admin` → step 4 may also call `create_next_action("issue-1001", ...)`, persisting the action and citing `next_actions`. These paths are exercised by the eval set ([eval-spec.md](eval-spec.md)).
