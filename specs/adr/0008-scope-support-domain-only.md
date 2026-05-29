# ADR-0008: Scope limited to the customer-support domain

- Status: Accepted
- Date: 2026-05-29

## Context

The brief ([brief.md](../../brief.md)) frames the business as "customer support and account management", but the **required** build is a minimal prototype: three roles (`sales_user`, `support_user`, `admin`), five tables (`customers`, `issues`, `issue_updates`, `next_actions`, `users`), and four agent capabilities (customer profile, open issues, issue history, next action).

An earlier iteration expanded the model to a second account-management domain (accounts, opportunities, regions), a fourth `operations` role, and revenue column masking. None of that is required by the brief. For a time-boxed assessment scored on **sound engineering judgement** and a **minimal working prototype**, the extra surface adds build-and-test cost and risk without addressing a stated requirement.

## Decision

Scope the prototype to the customer-support domain exactly as the brief requires:

- Entities: `customers`, `issues`, `issue_updates`, `next_actions`, `users`.
- Roles: `sales_user` (read-only), `support_user` (read + update issues), `admin` (full).
- Tools: `get_customer`, `list_open_issues`, `get_issue`, `summarise_issue_history`, `update_issue`, `create_next_action`.
- RBAC enforced by **operation** (read vs write), server-side in the tool layer ([rbac-matrix.md](../rbac-matrix.md)).

Account management (accounts, opportunities, regional scoping, column masking) and an `operations` oversight role are **deferred**, not designed out: the entity model and RBAC layer can extend to them later without rework.

## Consequences

Positive:
- Matches the brief precisely; less to build, seed, and evaluate in the assessment window.
- Simpler RBAC story (operation-based) that is easy to demonstrate and defend.
- Engineering judgement is visible: scope held to requirements.

Negative:
- The "account management" half of the business framing is not demonstrated in the prototype.
- Region-scoped reads and column masking — good RBAC showcases — are not exercised.

Mitigation: this ADR records the trade-off explicitly for the panel; the deferred scope is a clear next increment.

## Rejected alternatives

- **Two-domain, four-role model:** rejected for the prototype; exceeds the brief and adds risk for no required-credit. Revisit if account management becomes a requirement.
