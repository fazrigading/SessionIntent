# Linux Desktop Compatibility - Technical Engineering Plan

This document outlines a comprehensive architectural transition for SessionIntent to achieve full Linux desktop compatibility beyond the current GNOME/Wayland focus.

---

## 1. Provider Pattern for Display Abstraction

### Objective
Refactor `src/ui/display.py` to support multiple display protocols (Wayland, X11, TUI) through a provider pattern.

### Current State
- Current `src/ui/display.py` provides only text formatting utilities
- No abstraction for display server protocols

### Proposed Architecture

```
src/ui/
├── display/
│   ├── __init__.py          # Provider factory and registry
│   ├── base.py              # Abstract base class (DisplayProvider)
│   ├── wayland.py           # GNOME Shell / gdbus provider
│   ├── x11.py               # X11 / xdotool provider
│   ├── tui.py               # Terminal-based fallback
│   └── legacy.py             # Original formatting functions
```

### Implementation Details

**base.py - Abstract Provider**
```python
from abc import ABC, abstractmethod

class DisplayProvider(ABC):
    """Base class for all display providers."""

    @abstractmethod
    def format_mode_menu(self, modes: dict) -> str: ...

    @abstractmethod
    def format_mode_info(self, key: str, config: dict) -> str: ...

    @abstractmethod
    def select_mode_interactive(self, modes: dict) -> str | None: ...

    @abstractmethod
    def detect_environment(self) -> str: ...
```

**Provider Selection Logic**
- Auto-detect based on environment variables (`XDG_SESSION_TYPE`, `DESKTOP_SESSION`)
- Manual override via CLI flags: `--display wayland|x11|tui`
- Fallback chain: Wayland → X11 → TUI

**TUI Provider (Robust Fallback)**
The TUI provider ensures core functionality in headless or unsupported environments:

```python
class TUIDisplayProvider(DisplayProvider):
    """Terminal-based fallback for headless environments."""

    def format_mode_menu(self, modes: dict) -> str:
        # Numbered list output (1: Label format)
        entries = []
        for i, (key, cfg) in enumerate(modes.items(), 1):
            label = cfg.get("label", key)
            entries.append(f"{i}: {label}")
        return "\n".join(entries)

    def format_mode_info(self, key: str, config: dict) -> str:
        # Structured text output
        lines = [f"Mode: {key}"]
        if label := config.get("label"):
            lines.append(f"Label: {label}")
        if desc := config.get("description"):
            lines.append(f"Description: {desc}")
        return "\n".join(lines)

    def select_mode_interactive(self, modes: dict) -> str | None:
        # Read from stdin (compatible with scripts/pipes)
        menu = self.format_mode_menu(modes)
        print(f"Select mode:\n{menu}")
        try:
            choice = int(input("> ")) - 1
            keys = list(modes.keys())
            if 0 <= choice < len(keys):
                return keys[choice]
        except (ValueError, IndexError):
            pass
        return None

    def detect_environment(self) -> str:
        return "tui"
```

### Affected Files
- `src/ui/display.py` → refactored to `src/ui/display/legacy.py`
- `src/ui/selector.py` → updated to use provider
- `src/cli/parser.py` → add `--display` flag

---

## 2. Universal Workspace Manager

### Objective
Implement `src/workspace/manager.py` with EWMH and wlroots support to work across window managers.

### Current State
- Uses GNOME-specific `gdbus` calls
- Tightly coupled to GNOME Shell API

### Proposed Architecture

```
src/workspace/
├── __init__.py              # Factory and public API
├── base.py                  # WorkspaceProvider abstract class
├── gnome.py                 # GNOME Shell (existing gdbus)
├── kde.py                   # KDE Plasma (qdbus)
├── hyprland.py              # Hyprland (IPC socket)
├── sway.py                  # Sway (swaymsg)
├── wayland_generic.py      # Generic wlroots (wlr-foreign-toplevel)
├── ewmh.py                  # Generic EWMH (wmctrl, xdotool)
└── manager.py               # Legacy compatibility shim
```

### Implementation Details

**Subprocess-Based External Tool Integration**
All external tool invocations use Python's `subprocess` module - no new library dependencies:

```python
import subprocess
from typing import Any

class KDEWorkspaceProvider(WorkspaceProvider):
    """KDE Plasma workspace management via qdbus."""

    def switch_workspace(self, num: int) -> bool:
        try:
            subprocess.run(
                ["qdbus", "org.kde.KWin", "/KWin", "setCurrentDesktop", str(num)],
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_current_workspace(self) -> int | None:
        try:
            result = subprocess.run(
                ["qdbus", "org.kde.KWin", "/KWin", "currentDesktop"],
                capture_output=True,
                text=True,
                check=True,
            )
            return int(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
```

**Hyprland IPC Socket Provider** (Priority 2)
```python
class HyprlandWorkspaceProvider(WorkspaceProvider):
    """Hyprland workspace management via Unix socket IPC."""

    def __init__(self):
        socket_path = self._get_socket_path()

    def _get_socket_path(self) -> str | None:
        sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
        if sig:
            return f"/tmp/hypr/{sig}/.sock"
        return None

    def switch_workspace(self, num: int) -> bool:
        try:
            subprocess.run(
                ["hyprctl", "workspace", str(num)],
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
```

**Generic Wayland Support** (Priority 3 - wlroots)
Leverages `wlr-foreign-toplevel-management` protocol for wlroots-based compositors:

```python
class WaylandGenericProvider(WorkspaceProvider):
    """Generic wlroots support via wlr-foreign-toplevel-management.

    Supports: Hyprland, Sway, River, Labwc, and other wlroots compositors.
    """

    def __init__(self):
        self._protocol_available = self._check_protocol()

    def _check_protocol(self) -> bool:
        # Check for compositor-specific socket paths
        for sock in ["/run/user/1000/wayland-1", "/run/user/1000/sway-ipc*"]:
            if glob.glob(sock):
                return True
        return False
```

**EWMH Fallback** (Priority 4)
```python
class EWMHWorkspaceProvider(WorkspaceProvider):
    """Generic EWMH support via wmctrl and xdotool."""

    def switch_workspace(self, num: int) -> bool:
        try:
            subprocess.run(
                ["wmctrl", "-s", str(num - 1)],  # 0-indexed
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
```

**Provider Interface**
```python
class WorkspaceProvider(ABC):
    @abstractmethod
    def switch_workspace(self, num: int) -> bool: ...

    @abstractmethod
    def get_current_workspace(self) -> int | None: ...

    @abstractmethod
    def get_workspace_count(self) -> int: ...

    @abstractmethod
    def get_workspace_names(self) -> list[str]: ...

    @abstractmethod
    def move_window_to_workspace(self, window_id: str, workspace: int) -> bool: ...
```

### Priority Order (Revised)
1. **KDE Plasma** (qdbus) - Priority 1
2. **Hyprland** (IPC socket) - Priority 1
3. **Generic Wayland** (wlroots) - Priority 2
4. **Sway** (swaymsg) - Priority 2
5. **GNOME** (gdbus) - existing
6. **Generic EWMH** (wmctrl/xdotool) - fallback

---

## 3. Automated Session Detection System

### Objective
Automatically detect and load the appropriate backend at runtime based on the desktop environment.

### XDG Base Directory Specification Compliance

All configuration paths must resolve through XDG environment variables:

```python
import os

# XDG-compliant configuration paths
XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
XDG_DATA_HOME = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
XDG_STATE_HOME = os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state"))

CONFIG_DIR = Path(XDG_CONFIG_HOME) / "sessionintent"
DATA_DIR = Path(XDG_DATA_HOME) / "sessionintent"
STATE_DIR = Path(XDG_STATE_HOME) / "sessionintent"
```

**Detection Strategy**

**Environment Variable Detection (Priority Order)**
1. `XDG_SESSION_TYPE` - `wayland`, `x11`, `tty`
2. `DESKTOP_SESSION` - desktop environment name
3. `SWAYSOCK` - Sway socket presence
4. `HYPRLAND_INSTANCE_SIGNATURE` - Hyprland socket
5. `KDE_FULL_SESSION` - KDE Plasma

**Command Availability Detection**
```python
def _check_tool_available(tool: str) -> bool:
    """Check if an external tool is available on PATH."""
    return shutil.which(tool) is not None

# Tool availability matrix
AVAILABLE_TOOLS = {
    "gdbus": _check_tool_available("gdbus"),
    "qdbus": _check_tool_available("qdbus"),
    "hyprctl": _check_tool_available("hyprctl"),
    "swaymsg": _check_tool_available("swaymsg"),
    "wmctrl": _check_tool_available("wmctrl"),
    "xdotool": _check_tool_available("xdotool"),
}
```

**Detection API**
```python
@dataclass
class DesktopProfile:
    session_type: str          # wayland, x11, tty
    desktop: str               # gnome, kde, hyprland, sway, i3, etc.
    wm_type: str               # mutter, kwin, hyprland, sway, i3
    capabilities: set[str]     # Supported features
    config_dir: Path          # XDG-compliant config path
    tool_availability: dict[str, bool]  # Available external tools


def detect_desktop_environment() -> DesktopProfile:
    """
    Detect the current desktop environment.

    Returns:
        DesktopProfile with type, version, and capabilities
    """
    # 1. Check environment variables
    session_type = os.environ.get("XDG_SESSION_TYPE", "unknown")
    desktop = os.environ.get("DESKTOP_SESSION", "unknown")

    # 2. Check socket/instance signatures
    hypr_sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    sway_sock = os.environ.get("SWAYSOCK")

    # 3. Check tool availability
    tools = {tool: shutil.which(tool) for tool in TOOL_REQUIREMENTS}

    # 4. Determine capabilities and priority
    capabilities = _determine_capabilities(session_type, desktop, tools)

    return DesktopProfile(
        session_type=session_type,
        desktop=desktop,
        wm_type=_resolve_wm_type(desktop, hypr_sig, sway_sock),
        capabilities=capabilities,
        config_dir=Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")) / "sessionintent",
        tool_availability=tools,
    )
```

### Implementation Location
- `src/session/detector.py` - new module
- Integration with `SessionManager` initialization

### Fallback Behavior
- If detection fails, default to TUI mode
- Log warning with diagnostic information
- Allow manual override via CLI (`--force-backend`)

---

## 4. Desktop-Agnostic Extensions Manager

### Objective
Refactor `src/extensions/manager.py` to support multiple desktop environments beyond GNOME.

### Current State
- GNOME Shell extension-specific (UUIDs, `gnome-extensions` CLI)
- Hardcoded to GNOME ecosystem

### Proposed Architecture

```
src/extensions/
├── __init__.py              # Unified API
├── base.py                  # ExtensionProvider abstract class
├── gnome.py                 # GNOME Shell extensions
├── kde.py                   # KDE Plasma widgets/plasma-engine
├── plugins/                 # Desktop-agnostic plugins
│   ├── __init__.py
│   ├── base.py              # Plugin base class
│   └── system.py            # Existing system plugins
├── manager.py               # Legacy API compatibility
└── registry.py              # Extension/Plugin registry
```

### Implementation Details

**Extension Provider Interface**
```python
class ExtensionProvider(ABC):
    @abstractmethod
    def list_extensions(self) -> list[str]: ...

    @abstractmethod
    def get_extension_info(self, ext_id: str) -> dict | None: ...

    @abstractmethod
    def enable_extension(self, ext_id: str) -> tuple[bool, str]: ...

    @abstractmethod
    def disable_extension(self, ext_id: str) -> tuple[bool, str]: ...

    @abstractmethod
    def apply_config(self, config: dict) -> list[str]: ...
```

**KDE Provider** (Priority 1 after GNOME)
```python
class KDEExtensionProvider(ExtensionProvider):
    """KDE Plasma extension provider via qdbus and kpackagetool."""

    def list_extensions(self) -> list[str]:
        try:
            result = subprocess.run(
                ["kpackagetool5", "--list", "-t", "Plasma/Applet"],
                capture_output=True,
                text=True,
                check=True,
            )
            return [line.strip() for line in result.stdout.split("\n") if line.strip()]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    def enable_extension(self, ext_id: str) -> tuple[bool, str]:
        try:
            subprocess.run(
                ["kpackagetool5", "--install", ext_id],
                capture_output=True,
                check=True,
            )
            return True, f"Enabled: {ext_id}"
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return False, str(e)
```

**Plugin System Extension**
- Keep existing `src/plugins/system.py` for system-level operations
- Add plugin manifest format for third-party extensions
- Support hot-reload of plugins via importlib

### Refactoring Steps
1. Extract GNOME-specific code to `gnome.py`
2. Add `ExtensionProvider` base class
3. Create KDE provider
4. Update `apply_extensions()` to use provider pattern
5. Deprecate direct function calls in favor of provider

---

## 5. Testing Matrix

### Objective
Ensure stability across different window managers and distributions through comprehensive testing.

### Test Categories

#### Unit Tests
- Provider interfaces
- Detection logic
- Configuration parsing (XDG paths)
- Template resolution

#### Integration Tests

**Desktop Environment Matrix**

| Desktop | Session | Workspace Manager | Extensions | Priority |
|---------|---------|-------------------|------------|----------|
| KDE Plasma 6 | Wayland | qdbus | kpackagetool | P1 |
| Hyprland | Wayland | hyprctl IPC | N/A | P1 |
| GNOME 45+ | Wayland | gdbus | gnome-extensions | Current |
| Sway | Wayland | swaymsg | N/A | P2 |
| Generic wlroots | Wayland | wlr-foreign-toplevel | N/A | P2 |
| GNOME 45+ | X11 | gdbus | gnome-extensions | P2 |
| i3 | X11 | i3-msg | N/A | P2 |
| Generic EWMH | X11 | wmctrl/xdotool | N/A | Fallback |

#### Distribution Tests

| Distribution | Version | Desktop | Notes |
|--------------|---------|---------|-------|
| Fedora | 40, 41 | GNOME, KDE | Primary |
| Ubuntu | 24.04 | GNOME, KDE | LTS |
| Arch Linux | Rolling | All | AUR testing |
| Debian | 12 | GNOME | Stable |
| openSUSE | Tumbleweed | KDE, GNOME | Multi-DE |

### Test Infrastructure

**Test Fixtures**
```python
# tests/fixtures/desktop.py
@pytest.fixture
def mock_gnome_environment():
    """Mock GNOME + Wayland environment."""
    return {
        "XDG_SESSION_TYPE": "wayland",
        "DESKTOP_SESSION": "gnome",
        "WAYLAND_DISPLAY": "wayland-0",
    }

@pytest.fixture
def mock_kde_environment():
    """Mock KDE Plasma environment."""
    return {
        "XDG_SESSION_TYPE": "wayland",
        "DESKTOP_SESSION": "plasma",
        "KDE_FULL_SESSION": "true",
    }

@pytest.fixture
def mock_hyprland_environment():
    """Mock Hyprland environment."""
    return {
        "XDG_SESSION_TYPE": "wayland",
        "DESKTOP_SESSION": "hyprland",
        "HYPRLAND_INSTANCE_SIGNATURE": "test-sig",
    }
```

**CI/CD Pipeline**
- GitHub Actions matrix: `ubuntu-latest`, `fedora-latest`
- Containerized testing with Docker/Podman for multi-DE testing
- Manual testing checklist for each DE

---

## Implementation Phases (Revised)

### Phase 1: Foundation (Weeks 1-2)
- [ ] Implement XDG-compliant config paths in `src/constants/paths.py`
- [ ] Create detection system in `src/session/detector.py`
- [ ] Add CLI flags for manual override (`--force-backend`)
- [ ] Create TUI provider as universal fallback

### Phase 2: KDE & Hyprland Priority (Weeks 3-4)
- [ ] Refactor `src/workspace/manager.py` to provider pattern
- [ ] Implement KDE workspace provider (qdbus)
- [ ] Implement Hyprland workspace provider (IPC socket)
- [ ] Add KDE extension provider

### Phase 3: wlroots & Sway (Weeks 5-6)
- [ ] Add generic Wayland provider (wlr-foreign-toplevel)
- [ ] Implement Sway workspace provider (swaymsg)
- [ ] Test on wlroots compositors (River, Labwc)

### Phase 4: EWMH & Polish (Weeks 7-8)
- [ ] Implement EWMH fallback provider (wmctrl/xdotool)
- [ ] Create comprehensive test matrix
- [ ] CI integration
- [ ] Documentation

---

## Backward Compatibility

- Maintain `dev_mode` flag for all new providers
- Preserve CLI API compatibility
- Provide migration path for existing configs to XDG paths
- Deprecation warnings for removed features

---

## Dependencies

### External Tools (Runtime Dependencies)
These tools must be installed on the target system:

| Tool | Purpose | Used By |
|------|---------|---------|
| `gdbus` | GNOME D-Bus | GNOME provider |
| `qdbus` | KDE D-Bus | KDE provider |
| `hyprctl` | Hyprland control | Hyprland provider |
| `swaymsg` | Sway control | Sway provider |
| `wmctrl` | EWMH operations | EWMH provider |
| `xdotool` | X11 window ops | EWMH provider |

### Python Standard Library Only
- `subprocess` - All external tool invocations
- `os`, `pathlib` - XDG path handling
- `shutil` - Tool availability checking
- `abc` - Abstract base classes
- `dataclasses` - DesktopProfile definition

**No new Python package dependencies required.**

---

## Error Handling Strategy

All providers implement consistent error handling:

```python
class ProviderError(Exception):
    """Base exception for provider errors."""
    pass

class ToolNotFoundError(ProviderError):
    """Raised when required external tool is not found."""
    pass

class OperationFailedError(ProviderError):
    """Raised when provider operation fails."""
    pass

# Usage in providers
def switch_workspace(self, num: int) -> bool:
    try:
        subprocess.run([...], capture_output=True, check=True)
        return True
    except FileNotFoundError:
        raise ToolNotFoundError(f"Required tool not found") from None
    except subprocess.CalledProcessError as e:
        raise OperationFailedError(f"Operation failed: {e.stderr}") from None
```