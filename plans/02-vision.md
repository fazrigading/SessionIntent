# 02 — Target Architecture

This document defines the target architecture for SessionIntent after the rework. It is
the "to-be" counterpart to the "as-is" in `01-audit.md`.

## 1. Design principles

1. **Truthful docs** — documentation describes implemented behavior; anything not yet
   implemented is clearly marked as future work.
2. **Single source of truth** — exactly one template resolver, one app-loading path, one
   config schema, and one version source.
3. **Provider abstraction at the system boundary** — workspace management, display/UI,
   app detection, notifications, and extensions sit behind interfaces so desktop
   environments can be added without touching orchestration.
4. **Wired or removed** — every module is reachable from the main flow or is deleted. No
   "future" dead code lives in `src/`.
5. **XDG compliance** — all paths resolve through `XDG_CONFIG_HOME`, `XDG_DATA_HOME`,
   and `XDG_STATE_HOME` with correct fallbacks.

## 2. Package layout

Migrate from the current flat `src.` package to a clean namespace
`src/sessionintent/`. This is a breaking change to imports but the standard, obvious
layout for a modern Python project and it simplifies packaging.

```
src/sessionintent/
├── __init__.py            # public API + __version__ (single source)
├── __main__.py            # entry point
├── cli.py                 # argparse + dispatch (replaces src/cli/parser.py)
├── config.py              # load/merge/validate + schema (replaces src/config/)
├── constants.py           # XDG paths (replaces src/constants/)
├── models.py              # dataclasses: Config, Mode, AppSpec, WorkspaceSpec
├── hardware.py            # power detection (replaces src/hardware/power.py)
├── app.py                 # registry + launch/reuse + template (replaces src/app/)
├── session.py             # SessionManager (replaces src/session/manager.py)
├── state.py               # state persistence
├── notify.py              # notifications (wired in)
├── plugins.py             # plugin system (wired in)
└── providers/
    ├── __init__.py        # factory + registry
    ├── base.py            # ABCs + ProviderError hierarchy
    ├── detect.py          # desktop environment detection (XDG + tool probing)
    ├── workspace/
    │   ├── gnome.py       # GNOME extension socket + gdbus (existing logic moved)
    │   ├── ewmh.py        # wmctrl/xdotool fallback
    │   └── ...            # kde/hyprland/sway in later phases
    ├── display/
    │   ├── rofi.py        # wofi/rofi selector (existing logic moved)
    │   ├── tui.py         # terminal fallback
    │   └── ...            # per-DE as needed
    └── extensions/
        ├── gnome.py       # gnome-extensions (existing logic moved)
        └── ...
```

Rationale for the namespace change: `src` is a confusing package name, and
`sessionintent = "sessionintent.__main__:main"` is clearer than
`sessionintent = "src.__main__:main"`. The move also lets the `providers/` package sit
naturally next to the orchestration modules.

The GNOME Shell extension itself (`extensions/sessionintent-ws/`) remains the GNOME
workspace provider implementation. It is not a Python module; the provider wraps its
socket protocol and falls back to `gdbus`.

## 3. Provider interfaces

Providers are the portability seam. Each interface captures behavior that already exists
in a GNOME-specific form, so the port is mechanical.

### 3.1 Workspace provider

```python
class WorkspaceProvider(Protocol):
    def switch_workspace(self, num: int, monitor: str | None = None) -> bool: ...
    def get_current_workspace(self) -> int | None: ...
    def get_workspace_count(self) -> int: ...
    def wait_for_workspace(self, target: int, timeout: float) -> bool: ...
    def wait_for_window(self, app_pattern: str, target_workspace: int, timeout: float) -> bool: ...
```

- `gnome.py`: ports the current socket + `gdbus` logic from `src/workspace/manager.py`.
- `ewmh.py`: implements the interface via `wmctrl`/`xdotool`.

### 3.2 Display provider

```python
class DisplayProvider(Protocol):
    def select_mode(self, modes: dict) -> str | None: ...
    def format_menu(self, modes: dict) -> list[str]: ...
    def find_selector(self) -> str | None: ...
```

- `rofi.py`: ports the current `wofi`/`rofi` selector.
- `tui.py`: a terminal fallback that reads a numbered selection from stdin.

### 3.3 Extension provider

```python
class ExtensionProvider(Protocol):
    def enable(self, ext_id: str) -> tuple[bool, str]: ...
    def disable(self, ext_id: str) -> tuple[bool, str]: ...
    def list(self) -> list[str]: ...
    def get_info(self, ext_id: str) -> dict | None: ...
    def apply(self, config: dict) -> list[str]: ...
```

- `gnome.py`: ports the current `gnome-extensions` logic from `src/extensions/manager.py`.

### 3.4 Desktop detection

```python
@dataclass
class DesktopProfile:
    session_type: str       # wayland, x11, tty
    desktop: str            # gnome, kde, hyprland, sway, i3, unknown
    wm_type: str            # mutter, kwin, hyprland, sway, i3, unknown
    capabilities: set[str]
    tool_availability: dict[str, bool]

def detect_desktop() -> DesktopProfile: ...
```

Detection is environment-driven (XDG variables) and tool-probed (`shutil.which`), with a
factory selecting the first provider whose requirements are satisfied. `--backend` is a
manual override.

## 4. Orchestration flow

The reworked `SessionManager` should never call GNOME-specific code directly. It should:

1. Resolve config and apps through a single loader.
2. Detect the `DesktopProfile` (or honor `--backend`).
3. Obtain workspace, display, and extension providers from the factory.
4. Run `apply_mode`, `quit`, `kill`, and friends through those providers.
5. Wire notifications and plugins so they participate (or remove them until they are
   implemented properly).

This is a strict layering improvement: orchestration depends on provider interfaces,
never on concrete desktop environments.

## 5. What does not change

- The `{var|default}` template syntax stays (it is used and tested).
- The conceptual model of modes, workspaces, and per-mode app params stays.
- The GNOME Shell extension stays as the GNOME workspace implementation.

See `03-cli-and-config.md` for the user-facing surfaces and `04-phases.md` for the
ordered migration.
