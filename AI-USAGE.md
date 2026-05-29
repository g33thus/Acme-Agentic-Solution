# AI Tool Usage

How AI coding tools were used on this project, and how their output was governed. Required by the brief (deliverable #5).

Tool: Claude Code (Anthropic), used interactively with a human reviewing every step.

## What was delegated to AI, and why

- **Spec-driven scaffolding.** AI drafted the spec set from the brief: constitution, requirements, plan, ADRs, RBAC matrix, tool contracts, data schema, eval set, and the FastAPI/Docker scaffold. Specs were written before code so intent is explicit and reviewable.
- **Repetitive, mechanical edits.** Propagating a model change across many files (entity names, role lists, tool lists) and keeping cross-references consistent.
- **Boilerplate.** Docker Compose, `pyproject.toml`, config loader, health endpoint, `.env.example`.
- **Critique on demand.** AI was asked to argue against its own output from a product-owner and engineering-lead view, which surfaced real issues (see below).

Why: these are high-volume, low-ambiguity tasks where AI is fast and a human can verify the result quickly.

## How AI output was reviewed and validated

- **Specs are the source of truth.** Every behavioural claim must trace to a spec; code that contradicts a spec is a defect (constitution VIII).
- **Read every diff.** No change was accepted unseen.
- **Cross-reference checks.** Spec links and shared vocabulary (roles, entities, tools) were swept for stale terms after each model change.
- **Machine validation where possible.** JSON (eval dataset) validated; the spec-sync hook reminds the agent to reconcile specs after non-spec edits.
- **Brief as the yardstick.** The plan was reviewed back against `brief.md` to confirm coverage and catch scope drift.

## Errors and issues caught, and how

- **Self-contradicting specs.** An expansion left two different data models in the repo at once (customer/issue vs accounts/opportunities, three roles vs four). Caught by reading the files against each other; resolved by choosing one source of truth.
- **Scope creep beyond the brief.** AI expanded the model to a second domain and a fourth role the brief never asked for. Caught by reviewing against `brief.md`; reversed by an explicit human decision to trim to the support domain ([specs/adr/0008-scope-support-domain-only.md](specs/adr/0008-scope-support-domain-only.md)).
- **Stale scaffold.** Generated README and config lagged a model change. Caught in review; aligned and a floating model tag was pinned for reproducible evaluation.
- **A config hook was silently dropped** during an unrelated edit. Caught by re-reading the file before commit.

## What was kept under human control

- **Scope and product decisions.** What is in or out of the prototype (e.g. account management deferred, UI kept) was decided by a human, not the model.
- **Security claims.** Token validation, RBAC enforcement, prompt-injection handling, and trace redaction are specified, but a human must verify the implementation actually enforces them. Server-side authorisation is never trusted to "the prompt".
- **Final acceptance.** "Done" means verified against the specs and the brief by a human, not asserted by the model.
- **Anything irreversible or outward-facing.** Commits, deletions, and configuration changes were made only on explicit instruction.

## One-line summary

AI accelerated drafting and mechanical consistency; a human owned scope, security, and acceptance, and reviewed every change against the specs and the brief.
