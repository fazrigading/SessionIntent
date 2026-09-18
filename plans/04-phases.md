# 04 — Ordered Workstreams

This is the execution plan, broken into phases that follow the **stabilize-then-expand**
strategy. Each phase has concrete acceptance criteria so completion is verifiable.

## Phase 0 — Planning (this folder)

Deliver the `plans/` set and freeze the decisions in `07-decisions-and-risks.md`.

**Acceptance:**

- All 8 files in `plans/` exist and cross-link correctly.
- The audit is traceable to real file paths.
- Decisions are recorded once and referenced elsewhere.

## Phase 1 — Stabilize (no new features)

Fix what is broken before adding anything.

1. Fix the bugs listed in `01-audit.md` section 2:
   - Single source of truth for `__version__`.
   - Implement `--version` output.
   - Wire `--force` and `--no-cache` through to the scanner.
   - Fix the `wmctrl` typo in `src/session/snapshot.py`.
   - Consolidate the duplicated `resolve_template`.
   - Consolidate `AppRegistry` into `config.load_apps()`.
2. Remove dead/unwired code or wire it. Default is to **remove** scheduler, theme,
   watcher, and the unused `AppRegistry`; they can return later as properly wired
   features. See `07-decisions-and-risks.md` decision 4.
3. Fix CI:
   - Point `ci.yml` at `src/` and `tests/`.
   - Remove references to the nonexistent `sessionintent.py` and `requirements.txt`.
   - Use `ruff check src/ tests/`, `mypy src/`, and `pytest`.
4. Fix packaging:
   - Repair `packaging/fedora/sessionintent.spec` (version, paths, `%{_datadir}` typo).
   - Make `INSTALL.sh` install the real `src/` package via `pip install .`.
   - Populate or delete the empty `packaging/Arch/` and `scripts/` directories.
5. Make documentation truthful (coordinate with `06-documentation.md`).

**Acceptance:**

- `python3 -m pytest` passes.
- `ruff check src/ tests/` passes.
- `mypy src/` passes.
- `pip install .` produces a working `sessionintent`.
- `sessionintent --version` prints the correct version.

## Phase 2 — Architecture rework

Introduce the target architecture without changing user-facing behavior.

1. Create the `src/sessionintent/` namespace (see `02-vision.md`).
2. Add the `providers/` skeleton with `base.py` interfaces and error types.
3. Port existing logic into providers without behavior change:
   - GNOME workspace provider (extension socket + `gdbus`).
   - `wofi`/`rofi` display provider.
   - GNOME extension provider.
4. Add `detect.py` returning a `DesktopProfile` and a provider factory.
5. Add the TUI display provider as a universal fallback.
6. Rewire `SessionManager` to go through providers only.

**Acceptance:**

- Same CLI behavior as the end of Phase 1, but orchestration is provider-driven.
- Dev mode still works.
- Unit tests pass under the new namespace (re-homed imports).

## Phase 3 — Multi-desktop expansion

Add providers in priority order:

1. KDE (qdbus).
2. Hyprland (hyprctl / IPC socket).
3. Sway (swaymsg).
4. Generic EWMH (wmctrl / xdotool).
5. Generic wlroots.

Also:

- Expand detection coverage for these environments.
- Wire `--backend` as a manual override.
- Expand the test matrix (see `05-testing-and-ci.md`).

**Acceptance:**

- A `DesktopProfile` is selected automatically per environment.
- At minimum the EWMH and TUI paths have unit tests using mocked tools.
- Provider selection is fully unit-testable.

## Phase 4 — CLI/config redesign + docs refresh

Land the breaking changes from `03-cli-and-config.md`:

1. Implement the subcommand CLI.
2. Implement `version: 2` config schema and validation.
3. Add a `version: 1` → `version: 2` migration path.
4. Rewrite documentation to match (see `06-documentation.md`).
5. Publish a migration guide.

**Acceptance:**

- The flag-to-command mapping table is implemented.
- `sessionintent version` prints the version.
- `version: 2` configs load and validate; `version: 1` configs produce a clear migration
  message.
- Docs describe the new CLI and schema, not the old flags.

## Sequencing rationale

Stabilization (Phase 1) is first because the current CI and packaging are broken, so any
further work would be unverifiable. The architecture rework (Phase 2) comes before
multi-desktop (Phase 3) because providers are the prerequisite for adding environments.
The breaking CLI/config changes (Phase 4) are last so they land as one coordinated
change after the codebase is stable and provider-driven.
