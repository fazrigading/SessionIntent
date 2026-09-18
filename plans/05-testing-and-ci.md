# 05 — Testing, CI/CD, and Packaging

This document covers how the rework is verified and how the currently broken CI and
packaging are repaired.

## 1. Test strategy

Keep the existing `tests/` directory but re-home imports for the new
`src/sessionintent/` namespace during Phase 2.

### 1.1 Unit tests

| Area | Coverage |
|------|----------|
| Config | Loading, merging, schema validation (including negative cases). |
| Template | `{var|default}` resolution, edge cases, default fallback. |
| State | Save, load, clear. |
| Hardware | AC/battery detection with mocked `/sys` reads. |
| Detection | `DesktopProfile` selection under mocked env vars and tool availability. |
| Providers | Each provider's command construction with mocked `subprocess`. |
| App controller | Launch/reuse logic with mocked `is_running` and process spawning. |

### 1.2 Integration (dev-mode) tests

- `apply_mode` runs in dev mode and emits the expected dry-run commands.
- `quit`, `kill`, `suspend`, `panic`, `clear`, `status`, `list` behave correctly.
- Full flow: select a mode (mocked selector) → apply → save state.

### 1.3 Desktop matrix

This is a plan for validation, not a claim that everything is automated today.

| Desktop | Session | Workspace provider | Extension provider | Coverage |
|---------|---------|--------------------|--------------------|----------|
| GNOME | Wayland | `gnome` (extension socket + gdbus) | `gnome` (gnome-extensions) | Automated (mocked) |
| GNOME | X11 | `gnome` (gdbus) | `gnome` | Automated (mocked) |
| KDE Plasma | Wayland/X11 | `kde` (qdbus) | `kde` (kpackagetool) | Automated (mocked) |
| Hyprland | Wayland | `hyprland` (hyprctl) | N/A | Automated (mocked) |
| Sway | Wayland | `sway` (swaymsg) | N/A | Automated (mocked) |
| Generic wlroots | Wayland | `wlroots` | N/A | Manual |
| Generic EWMH | X11 | `ewmh` (wmctrl/xdotool) | N/A | Automated (mocked) |
| TUI fallback | Any | N/A | N/A | Automated |

"Automated (mocked)" means unit tests that fake external tool availability and output.
Real-device testing remains a manual checklist.

## 2. CI/CD fixes

The current `.github/workflows/ci.yml` is broken because it references files that do not
exist. The repaired workflow should run, in order:

1. `ruff check src/ tests/`
2. `mypy src/`
3. `pytest`

### 2.1 Dependency handling

Either add a `requirements.txt` or move dev dependencies into `pyproject.toml` as an
optional dependency group. The latter is preferred to avoid a second source of truth.

### 2.2 Release workflow

The COPR job in `.github/workflows/release.yml` runs `copr build` against `dist/*.rpm`,
which never exists because the workflow only builds a wheel via `python -m build`. Fix it
to either build the RPM via the spec or mark the COPR step as a manual, documented
follow-up rather than an automated step that silently no-ops.

## 3. Packaging fixes

### 3.1 RPM spec

Repair `packaging/fedora/sessionintent.spec`:

- Correct the version.
- Remove the `sessionintent.py` install line and install the `src/sessionintent` package.
- Fix the `%{_ datadir}` typo to `%{_datadir}`.

### 3.2 Installer

Fix `INSTALL.sh` to install the real package:

- Replace the nonexistent `sessionintent.py` copy with `pip install .` (or equivalent).
- Point example config installs at `examples/`, not the repo root.

### 3.3 Empty directories

`packaging/Arch/` and `scripts/` are empty. Either populate them with a working PKGBUILD
and real scripts, or remove them. Keeping empty directories implies planned work that
does not exist.

## 4. Definition of done for quality gates

A phase is not complete until:

- The relevant tests pass.
- `ruff` and `mypy` are clean.
- A local `pip install .` produces a working command.
- The CI workflow runs the same checks locally as it does in GitHub Actions.

See `04-phases.md` for phase-specific acceptance criteria and `06-documentation.md` for
keeping docs aligned with these guarantees.
