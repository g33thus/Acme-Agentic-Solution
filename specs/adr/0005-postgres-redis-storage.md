# ADR-0005: PostgreSQL for data, Redis for session memory

- Status: Accepted
- Date: 2026-05-29

## Context

The system needs durable structured storage for operational data and fast, expiring per-session conversation memory.

## Decision

Use PostgreSQL for structured operational data (customers, issues, issue_updates, next_actions, users) with role-scoped, parameterised reads and writes. Use Redis for per-session conversation memory keyed by authenticated session id, with a configurable TTL.

## Consequences

Positive:
- Relational integrity and scoped querying for RBAC (principle VI).
- Fast session reads/writes and automatic expiry via Redis TTL.
- Both open-source and local.

Negative:
- Two stores to operate and back up.
- Session and durable data must not blur; memory stays in Redis only.

## Rejected alternatives

- Single store for both: rejected; mismatched access patterns and expiry needs.
- In-process memory: rejected; lost on restart, no cross-process sharing.
