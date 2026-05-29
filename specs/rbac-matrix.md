# RBAC Matrix

Concrete authorisation rules for every role against every entity and operation. Governed by [constitution.md](constitution.md) (II, VI). Implements [spec.md](spec.md) §2 and FR-3.3/3.4. Feeds build task T-1.4.

Roles come from Keycloak token claims and are enforced **server-side in the data layer**, never client-side (constitution VI). Every MCP tool ([tools.md](tools.md)) checks the rule below before reading or writing.

## 1. Roles

Three roles, matching the client brief:

| Role | Intent |
|------|--------|
| `sales_user` | Read-only access to customer and issue data |
| `support_user` | Read and update access for issues, including adding updates |
| `admin` | Full access, including creating and updating next actions, and user management |

## 2. Operations matrix

Rows are operations, columns are roles. `R` = read, `W` = write, `—` = denied.

| Operation | Entity | `sales_user` | `support_user` | `admin` |
|-----------|--------|--------------|----------------|---------|
| Read customer profile | customers | R | R | R |
| Read issues / open issues | issues | R | R | R |
| Read issue history | issue_updates | R | R | R |
| Update issue (status) | issues | — | W | W |
| Add issue update | issue_updates | — | W | W |
| Create next action | next_actions | — | — | W |
| Update next action | next_actions | — | — | W |
| Read next actions | next_actions | R | R | R |
| Manage users | users | — | — | W |

## 3. Row scope

v1 is single-tenant for internal staff: all three roles may read all customers and issues. Scope is enforced by **operation** (read vs write), not by row partitioning. Write attribution is recorded (`issue_updates.author_id`, `next_actions.created_by`) for audit (constitution IV).

## 4. Rule-to-tool mapping

Each rule is enforced by the tool that performs it. See [tools.md](tools.md).

| Rule | Enforcing tool(s) |
|------|-------------------|
| any role reads customers | `get_customer` |
| any role reads issues / open issues | `list_open_issues`, `get_issue` |
| any role reads issue history | `summarise_issue_history` |
| only support_user/admin update issues | `update_issue` |
| only admin creates next actions | `create_next_action` |

## 5. Denial behaviour

A write attempt by an unauthorised role returns a **permission-scoped refusal**: the agent states the access boundary and performs no write (constitution III). At the API boundary a directly addressed forbidden operation maps to `403` per [api/openapi.yaml](api/openapi.yaml); within an agent answer it is a grounded "you do not have permission to do that" response. The negative case (`sales_user` attempting a write) is exercised by the eval set ([eval-spec.md](eval-spec.md)) and is an acceptance criterion ([spec.md](spec.md) §6).
