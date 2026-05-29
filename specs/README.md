# Specs: Acme Operations Agentic Assistant

Spec-driven development workspace. Code follows specs, never the reverse.

## How these specs fit together

| File | Purpose | Answers |
|------|---------|---------|
| [constitution.md](constitution.md) | Non-negotiable principles | What rules every decision must respect |
| [spec.md](spec.md) | Functional and non-functional requirements | What the system must do |
| [plan.md](plan.md) | Technical approach and component design | How we build it |
| [data-spec.md](data-spec.md) | Schema and fixed seed invariants | What the data looks like |
| [rbac-matrix.md](rbac-matrix.md) | Role × entity row/column rules | Who may read what |
| [tools.md](tools.md) | MCP tool input/output schemas | What the agent can do |
| [agent-spec.md](agent-spec.md) | Agent loop, bounds, grounding, scope safety | How the agent reasons and stays bounded |
| [security-spec.md](security-spec.md) | Token validation, prompt injection, trace redaction, session isolation | How the system stays secure |
| [skills/customer-escalation-summary.md](skills/customer-escalation-summary.md) | Reusable multi-step procedure | The named workflow |
| [eval-spec.md](eval-spec.md) | Acceptance tests and scoring | How we prove it works |
| [eval/dataset.json](eval/dataset.json) | Starter labelled test set | The cases we score against |
| [observability-spec.md](observability-spec.md) | Required spans and attributes | What every request must trace |
| [tasks.md](tasks.md) | Ordered, checkable build tasks | In what order we build it |
| [adr/](adr/) | Architecture Decision Records | Why we chose each major option |
| [api/openapi.yaml](api/openapi.yaml) | FastAPI contract | The exact API shape |

## Reading order

1. `constitution.md` — the rules.
2. `spec.md` — the requirements.
3. `plan.md` — the design.
4. `adr/` — the reasoning behind the design.
5. `api/openapi.yaml` — the API contract.
6. `data-spec.md` — the data model and seed.
7. `rbac-matrix.md` — the authorisation rules.
8. `tools.md` — the tool contracts.
9. `agent-spec.md` — how the agent reasons and stays bounded.
10. `security-spec.md` — the security controls.
11. `skills/` — the workflows.
12. `observability-spec.md` — the tracing contract.
13. `eval-spec.md` — the acceptance tests.
14. `tasks.md` — the build sequence.

## Update rule

Any change to behaviour, architecture, or API must update the matching spec in the same change. Specs and code stay in sync. A `.claude` hook reminds the agent to reconcile specs after edits. See the repository root configuration.

## Status

Phase: **specification**. No implementation code yet.
