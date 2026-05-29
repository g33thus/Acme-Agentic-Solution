# ADR-0004: Keycloak for auth and RBAC

- Status: Accepted
- Date: 2026-05-29

## Context

The system needs authentication and role-based access control without storing passwords, using open-source components (constitution principles II and VI).

## Decision

Use Keycloak as the OIDC provider. It issues bearer tokens carrying role claims (`sales_user`, `support_user`, `admin`). FastAPI validates tokens on every request and extracts roles. RBAC is enforced server-side in the tool and data layers, scoped per role. See [rbac-matrix.md](../rbac-matrix.md) for the rules and [security-spec.md](../security-spec.md) §1 for the validation checks (issuer, audience, signature, expiry).

## Consequences

Positive:
- Standard OIDC, no password handling in the app.
- Central role and user management.
- Open-source, runs locally.

Negative:
- Realm and client configuration adds setup effort.
- A role-to-data-scope matrix must be defined and maintained.

## Rejected alternatives

- Application-managed auth: rejected; password storage and weaker standards compliance.
- API keys only: rejected; no per-user identity or role granularity.
