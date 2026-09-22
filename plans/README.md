# SessionIntent Full Rework Plan

This folder holds the complete, multi-file plan for a full rework of SessionIntent. The
rework follows a **stabilize-then-expand** strategy: first fix the bugs, dead code, and
doc drift that currently exist; then refactor the internals behind a provider
abstraction; and finally expand to multiple Linux desktop environments.

The plan is written from the actual code in the repository, not from the aspirational
docs. Where the current documentation claims features that are not wired up, the audit
(`01-audit.md`) calls that out explicitly.

## Contents

| File | Purpose |
|------|---------|
| [`00-superseded-compatibility-plan.md`](00-superseded-compatibility-plan.md) | Original desktop-compat proposal (superseded, kept for history). |
| [`01-audit.md`](01-audit.md) | Current-state audit: real architecture, concrete bugs, dead code, doc drift. |
| [`02-vision.md`](02-vision.md) | Target architecture, design principles, package layout, provider interfaces. |
| [`03-cli-and-config.md`](03-cli-and-config.md) | Target CLI surface and config schema (breaking redesign). |
| [`04-phases.md`](04-phases.md) | Ordered workstreams with acceptance criteria. |
| [`05-testing-and-ci.md`](05-testing-and-ci.md) | Test strategy, CI/CD fixes, packaging fixes. |
| [`06-documentation.md`](06-documentation.md) | Documentation rewrite and consolidation plan. |
| [`07-decisions-and-risks.md`](07-decisions-and-risks.md) | Architecture decision records, trade-offs, and risks. |
| [`08-desktop-compatibility.md`](08-desktop-compatibility.md) | As-built record: what the compat plan became in code. |
| [`09-uv-packaging.md`](09-uv-packaging.md) | As-built record: uv installability (tool install, lockfile, CI, docs). |

## How to read this plan

- **01** is where we are today (the "as-is").
- **02** and **03** are where we are going (the "to-be" architecture and interfaces).
- **04** is how we get there, phase by phase.
- **05** is how we prove each phase is done.
- **06** is how we keep documentation truthful as the code changes.
- **07** is why we chose this path and what could go wrong.

Read in order: `01` → `02` → `03` → `04` → `05` → `06` → `07`. Each file links forward
and backward instead of duplicating content.

## Status tracker

| Phase | Status | Notes |
|-------|--------|-------|
| 0 — Planning | Done | Plan set frozen in this folder. |
| 1 — Stabilize | Done | Bugs fixed, dead code removed, CI/packaging repaired, docs truthful. Gates: 318 pytest passed, ruff/mypy clean, `pip install .` → `sessionintent 0.3.3`. |
| 2 — Architecture rework | Done | `src/sessionintent/` namespace + provider layer (providers, detection, TUI). Gates: 333 pytest passed, ruff/mypy clean. |
| 3 — Multi-desktop expansion | Done | KDE, Hyprland, Sway, wlroots-chain providers + KDE extensions; `--backend` override; mocked provider tests. Gates: 362 pytest passed, ruff/mypy clean. |
| 4 — CLI/config redesign + docs | Done | Subcommand CLI, `version: 2` schema + validation, v1 in-memory migration with notice, docs/MIGRATION.md, docs refresh. Gates: 359 pytest passed, ruff/mypy clean. |

## Conventions

- One topic per file; cross-link rather than duplicating.
- Decisions are recorded once in `07-decisions-and-risks.md` and referenced from
  elsewhere.
- File paths in this plan are relative to the repository root.
- Bug references are traceable to real files; line numbers may drift as the code
  changes, so treat them as pointers rather than fixed coordinates.
- "Wired" means a module is reachable from the main execution flow, not merely defined
  and exported.
