# Data Spec

The structured data model and the fixed seed dataset the eval set and acceptance criteria depend on. Governed by [constitution.md](constitution.md). Implements [spec.md](spec.md) FR-3.1 and feeds build tasks T-1.1 (schema) and T-1.3 (seed).

Durable structured data lives in PostgreSQL. The agent reads and writes it only through MCP tools ([tools.md](tools.md)), never raw SQL. Scope is enforced in the data layer per [rbac-matrix.md](rbac-matrix.md) and constitution VI.

## 1. Entities and relationships

```
customers ──1:*── issues ──1:*── issue_updates
                    │
                    └──1:*── next_actions

users  (carry role; not owned by customers)
```

- A `customer` is an Acme client organisation, looked up by name.
- An `issue` is an operational ticket raised against a customer.
- An `issue_update` is a timestamped note in an issue's history.
- A `next_action` is a recommended action created against an issue.
- A `user` is an internal Acme staff member with a role.

## 2. Schema (PostgreSQL)

Authoritative DDL. Build task T-1.1 must match this; T-1.2 turns it into migrations. The five tables map directly to the client's required schema (`customers`, `issues`, `issue_updates`, `next_actions`, `users`).

```sql
CREATE TABLE customers (
    id            TEXT PRIMARY KEY,          -- e.g. 'cust-x'
    name          TEXT NOT NULL UNIQUE,      -- lookup key, e.g. 'Client X'
    tier          TEXT,                      -- e.g. 'enterprise', 'mid', 'smb'
    region        TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id            TEXT PRIMARY KEY,          -- matches Keycloak subject
    username      TEXT NOT NULL UNIQUE,
    role          TEXT NOT NULL              -- one of: sales_user, support_user, admin
                  CHECK (role IN ('sales_user','support_user','admin')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE issues (
    id            TEXT PRIMARY KEY,          -- e.g. 'issue-1001'
    customer_id   TEXT NOT NULL REFERENCES customers(id),
    title         TEXT NOT NULL,
    status        TEXT NOT NULL              -- open, in_progress, resolved, closed
                  CHECK (status IN ('open','in_progress','resolved','closed')),
    priority      TEXT NOT NULL              -- low, medium, high, critical
                  CHECK (priority IN ('low','medium','high','critical')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE issue_updates (
    id            BIGSERIAL PRIMARY KEY,
    issue_id      TEXT NOT NULL REFERENCES issues(id),
    author_id     TEXT REFERENCES users(id), -- who added the note
    note          TEXT NOT NULL,             -- groundable history fact
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE next_actions (
    id            BIGSERIAL PRIMARY KEY,
    issue_id      TEXT NOT NULL REFERENCES issues(id),
    action        TEXT NOT NULL,             -- the recommended action
    rationale     TEXT,                      -- grounded justification
    status        TEXT NOT NULL DEFAULT 'proposed'
                  CHECK (status IN ('proposed','accepted','done','rejected')),
    created_by    TEXT NOT NULL REFERENCES users(id),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### RBAC-relevant columns

| Column | Used for |
|--------|----------|
| `users.role` | role of the caller, sourced from the Keycloak token, reconciled here |
| `issue_updates.author_id`, `next_actions.created_by` | write attribution and audit |

No column-level masking in v1; authorisation is by role and operation (read vs write) per [rbac-matrix.md](rbac-matrix.md).

## 3. Redis versus PostgreSQL

Required rationale per the client brief. See [ADR-0005](adr/0005-postgres-redis-storage.md).

| Store | Holds | Why |
|-------|-------|-----|
| PostgreSQL | customers, issues, issue_updates, next_actions, users | Durable system of record; relational integrity; audited writes; survives restart |
| Redis | per-session conversation memory, recent tool-call results (TTL) | Ephemeral, fast, expendable; scoped to a session; never the source of truth |

Trade-off: anything that must survive, be queried relationally, or be audited goes to PostgreSQL. Anything that is per-session, latency-sensitive, and safe to lose goes to Redis with a TTL. Conversation context lives in Redis because it is short-lived and tied to one session; operational facts live in PostgreSQL because answers must be grounded in them (constitution III) and writes must be durable and auditable (constitution IV).

## 4. Seed invariants

The local-dev and eval seed (build task T-1.3) is a **fixed contract**, not arbitrary sample data. The eval set ([eval-spec.md](eval-spec.md), [eval/dataset.json](eval/dataset.json)) and the acceptance criteria in [spec.md](spec.md) §6 depend on these holding. Changing them requires updating the eval set in the same change (constitution VIII).

### Customers
- `cust-x` ("Client X", tier `enterprise`) exists.
- `cust-y` ("Client Y", tier `mid`) exists.

### Users (one usable login per role)
- `u-sales` — role `sales_user`.
- `u-support` — role `support_user`.
- `u-admin` — role `admin`.

### Issues
- `issue-1001` — Client X, status `open`, priority `high`. Has ≥2 `issue_updates` (so `summarise_issue_history` is meaningful) and a non-null history trail.
- `issue-1002` — Client X, status `in_progress`, priority `medium`, with at least one update.
- `issue-2001` — Client Y, status `open`, priority `low`.

### Issue updates
- `issue-1001` has at least two updates with distinct `created_at`, the latest describing current status (groundable for a summary and citation).

### Next actions
- The `next_actions` table starts **empty** for `issue-1001`, so the admin "create next action" acceptance test produces an observable insert.

### Derived guarantees (used directly by eval cases)
1. `get_customer("Client X")` → returns `cust-x` profile.
2. `list_open_issues` for Client X → returns `issue-1001` (and any other open).
3. `summarise_issue_history("issue-1001")` → grounded summary citing real updates.
4. `u-admin` `create_next_action("issue-1001", ...)` → row inserted, returned with id.
5. `u-sales` attempting `update_issue` or `create_next_action` → scoped refusal, no write.
