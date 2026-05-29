# ADR-0003: MCP for tool exposure

- Status: Accepted
- Date: 2026-05-29

## Context

The agent must act only through declared, schema-validated tools (constitution principle V), never arbitrary code or raw SQL.

## Decision

Expose all tools through a Model Context Protocol (MCP) server. Each tool declares JSON input and output schemas. The agent discovers and invokes tools through MCP. Authorisation, validation, and tracing wrap every call.

## Consequences

Positive:
- Clear, typed contract between agent and capabilities.
- Central point to enforce RBAC, validation, and tracing.
- Tools reusable across agents and skills.

Negative:
- Extra moving part to run and version.
- Every new capability needs a tool definition.

## Rejected alternatives

- Direct function calling inside the app: rejected for weaker isolation and no standard contract.
- Letting the model emit SQL: rejected; violates principles V and VI.
