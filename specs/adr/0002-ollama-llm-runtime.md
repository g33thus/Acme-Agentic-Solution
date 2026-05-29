# ADR-0002: Ollama as the LLM runtime

- Status: Accepted
- Date: 2026-05-29

## Context

The agent needs local LLM inference (per [ADR-0001](0001-local-open-source-stack.md)) with tool-calling support and a simple operational model.

## Decision

Use Ollama to serve an open-source model locally. The agent talks to Ollama over its local HTTP API. The specific model is configurable and selected by evaluation, not hard-coded.

## Consequences

Positive:
- Simple local serving and model management.
- Swappable models without code change.
- No data leaves the host.

Negative:
- Reasoning and tool-selection quality bounded by local model and hardware.
- Requires the evaluation harness (FR-8) to gate model choice.

## Rejected alternatives

- Direct llama.cpp integration: rejected for higher integration effort.
- Hosted inference: rejected by [ADR-0001](0001-local-open-source-stack.md).
