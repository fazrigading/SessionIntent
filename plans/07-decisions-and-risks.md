# 07 — Decisions and Risks

This file records the architecture decisions made for the rework, their rationale, and
the risks that need to be managed. Other plan files reference these decisions rather than
restating them.

## 1. Architecture decision records

### ADR-1: Stabilize-then-expand over big-bang rewrite

**Decision:** Fix bugs, remove dead code, and repair CI/packaging first; add multi-desktop
capability only after the codebase is stable and provider-driven.

**Rationale:** The working GNOME extension and the existing test suite are assets. A
big-bang rewrite would discard those and expand the blast radius. Stabilizing first makes
every subsequent phase verifiable.

**Risk:** Perceived as slow because no new user-facing features land in Phase 1.

**Mitigation:** Phase 1 produces a working, honest baseline; Phases 2–3 deliver the
expansion that users actually want.

### ADR-2: Migrate namespace from `src.` to `src/sessionintent`

**Decision:** Move to the standard `src/sessionintent/` layout.

**Rationale:** `src` is a confusing package name, and the move simplifies packaging and
gives the `providers/` package a natural home.

**Risk:** Import churn across the codebase and tests.

**Mitigation:** Land the move in Phase 2 as a dedicated step with re-homed tests, and
gate it behind the existing quality checks.

### ADR-3: Keep the GNOME Shell extension, wrap it in a provider

**Decision:** Retain `extensions/sessionintent-ws/` as the GNOME workspace implementation
and wrap its socket protocol (plus `gdbus` fallback) behind the `WorkspaceProvider`
interface.

**Rationale:** The extension works on GNOME 46+ and is already the primary workspace
mechanism. The provider abstraction is the portability layer, so there is no need to
replace the extension.

**Risk:** Regression in the extension's socket protocol while moving the Python side into
a provider.

**Mitigation:** Port the existing logic mechanically without changing the socket commands,
and cover it with mocked unit tests.

### ADR-4: Delete unwired modules by default

**Decision:** Modules that are defined but not reachable from the main flow are removed
unless there is an explicit plan to wire them.

**Rationale:** Dead code and the docs that describe it are the main source of drift. It is
cheaper to re-add a feature on demand than to maintain unreachable code.

**Risk:** Removing a module someone intended to finish.

**Mitigation:** The audit (`01-audit.md`) records exactly which modules are unwired so
the decision is explicit and reversible.

### ADR-5: Breaking CLI/config changes are acceptable, but coordinated

**Decision:** The CLI moves to subcommands and the config schema bumps to `version: 2`.
Both land together in Phase 4.

**Rationale:** The current flat flags and unenforced schema cause bugs (unhandled
`--version`, ignored `--force`) and make extension awkward. A single coordinated breaking
change is better than incremental churn.

**Risk:** User friction.

**Mitigation:** Provide a flag-to-command migration table and a `version: 1` → `version: 2`
migration path.

### ADR-6: Provider priority order

**Decision:** Expand in the order GNOME (existing) → KDE → Hyprland → Sway → EWMH →
generic wlroots.

**Rationale:** KDE and Hyprland are the most requested targets, while EWMH and wlroots
serve as the broadest fallbacks.

**Risk:** Spreading effort across many backends without real-device testing.

**Mitigation:** Unit tests mock external tools; real-device testing remains a manual
checklist, clearly marked in the test matrix.

## 2. Open questions

These do not block Phase 1 but must be resolved before the relevant later phase:

1. **JSON Schema vs. explicit validator** for `version: 2` — both are viable; the choice
   affects the validation code and test fixtures.
2. **Config migration** — whether `version: 1` configs are auto-migrated in place or
   only reported with a migration guide.
3. **Plugin system scope** — whether the existing `Plugin` API is wired as-is, redesigned,
   or deferred again.
4. **Notification backend** — `pynotify` vs. `notify-send` vs. `dbus-send` as the primary
   path.
5. **RPM/COPR automation** — whether the release workflow builds the RPM from the spec or
   defers COPR to a manual step.

## 3. Risks and mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep | The rework grows beyond stabilize-then-expand. | Strict phase gates and acceptance criteria in `04-phases.md`. |
| GNOME extension regression | Workspace switching breaks on GNOME. | Mechanical port with unchanged socket protocol + mocked tests. |
| Namespace migration breakage | Imports and packaging fail. | Dedicated Phase 2 step, re-homed tests, CI gate. |
| Docs drift again | Docs overstate the code. | Docs and code changes land in the same phase (`06-documentation.md`). |
| Packaging/CI remains broken | Cannot verify any change. | Phase 1 fixes CI and packaging first. |
