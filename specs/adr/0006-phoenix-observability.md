# ADR-0006: Arize Phoenix for observability and evaluation

- Status: Accepted
- Date: 2026-05-29

## Context

Every action must be auditable (constitution principle IV) and no behaviour ships without evaluation (principle VII). Both must run locally and open-source.

## Decision

Use Arize Phoenix for tracing and evaluation. Instrument the API, agent, and tools with OpenTelemetry and export spans to Phoenix. Run the evaluation harness against Phoenix-stored traces and a labelled test set, scoring groundedness, correctness, and RBAC compliance.

## Consequences

Positive:
- Single tool for traces and evals.
- Standard OpenTelemetry instrumentation.
- Local and open-source.

Negative:
- Another service to run.
- Trace volume and retention need management.

## Rejected alternatives

- Logs only: rejected; no structured spans or eval support.
- Separate tracing and eval tools: rejected; more integration and context-switching.
