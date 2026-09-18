# 08 — Desktop Compatibility (As-Built Record)

This file replaces `LINUX_DESKTOP_COMPATIBILITY_PLAN.md` (now kept as
`plans/00-superseded-compatibility-plan.md`). That document was a proposal; this one records what
actually shipped across Phases 1–4 plus follow-ups, and where the
implementation deliberately deviates from the proposal.

## 1. What shipped

| Proposal | As-built |
|----------|----------|
| Display provider abstraction (`src/ui/display/`) | `src/sessionintent/providers/display/`: `rofi.py` (moved `wofi`/`rofi` selector verbatim), `tui.py` (stdin fallback) |
| Workspace provider tree (`src/workspace/`) | `src/sessionintent/providers/workspace/`: `gnome.py`, `kde.py`, `hyprland.py`, `sway.py`, `wlroots.py`, `ewmh.py` |
| Extension providers (`src/extensions/`) | `src/sessionintent/providers/extensions/`: `gnome.py`, `kde.py` (+ null provider) |
| `src/session/detector.py` | `src/sessionintent/providers/detect.py` (`DesktopProfile` + `get_providers()` factory) |
| `--display` / `--force-backend` flags | Single `--backend` global flag (`gnome`, `ewmh`, `kde`, `hyprland`, `sway`, `wlroots`) |
| `wlr-foreign-toplevel` generic provider | Best-effort chain instead (hyprctl → swaymsg → EWMH): no new dependencies, same coverage goal |

## 2. Deliberate deviations

1. **Namespace first.** The whole tree moved `src/` → `src/sessionintent/`
   (Phase 2) before any provider was added, so providers live next to
   orchestration instead of inside per-concern packages.
2. **Protocols, not ABCs.** Interfaces are `typing.Protocol` in
   `providers/base.py`, with a `ProviderError` /
   `ToolNotFoundError` / `OperationFailedError` hierarchy.
3. **GNOME is the default, not one peer among many.** Unknown desktops
   keep pre-provider GNOME behavior; nothing that worked in Phase 1
   regressed on a new desktop.
4. **`wait_for_window` lives in `ewmh.py`.** The xdotool wait is
   desktop-agnostic; the GNOME provider delegates to it.
5. **KDE enable/disable is a documented manual step.** Applets list via
   `kpackagetool6`/`5`; programmatic enable/disable is not reliably
   scriptable, so the provider reports the manual step instead of
   pretending (`KdeExtensionProvider`).
6. **No `get_workspace_names` / `move_window_to_workspace`.** Proposed
   interface methods with no caller were cut (YAGNI); `wait_for_workspace`
   / `wait_for_window` (which have callers) are in instead.
7. **XDG paths are user dirs only.** `CONFIG_DIR` honors
   `XDG_CONFIG_HOME`, `STATE_DIR` honors `XDG_STATE_HOME` (empty counts
   as unset). No `DATA_DIR`: nothing reads a user data dir.

## 3. Detection (as-built)

`detect_desktop(env)` reads, in order: `HYPRLAND_INSTANCE_SIGNATURE`,
`SWAYSOCK`, `KDE_FULL_SESSION`, then `XDG_SESSION_TYPE` /
`DESKTOP_SESSION`. Wayland + unknown DE + `WAYLAND_DISPLAY` present
resolves to the generic `wlroots` desktop. Tool availability is probed
with `shutil.which` over `TOOL_REQUIREMENTS`
(`gdbus`, `qdbus`, `hyprctl`, `swaymsg`, `wmctrl`, `xdotool`, `wofi`, `rofi`).

`get_providers(profile, dev_mode, backend)` maps desktops to providers;
display is `rofi` when a graphical selector exists, else TUI.
Unknown `backend` names raise `ProviderError`.

## 4. Verification status

- 387 unit tests, all mocked at the `subprocess` / env boundary; every
  provider has command-construction tests (`tests/test_providers/`).
- `ruff` and `mypy` clean; `pip install .` verified per phase.
- **Not done (needs real hardware):** River/Labwc runs, GNOME X11 run,
  distro matrix in `05-testing-and-ci.md`.

## 5. Remaining non-goals

- `flatpak-spawn` support for confined builds (see Flatpak manifest header).
- AUR / PPA / Flathub uploads (files exist: `packaging/`, `debian/`).
- Time-based switching, themes, config hot-reload: removed as unwired
  in Phase 1; return only as properly wired features.

See `04-phases.md` for the phase history and `07-decisions-and-risks.md`
for why each deviation was chosen.
