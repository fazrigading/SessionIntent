# SessionIntent Roadmap

This document outlines potential future enhancements and areas for community contribution.

## Stabilized Baseline (Phase 1)

The rework plan lives in `plans/` (see `plans/04-phases.md`). Phase 1 keeps
only what is wired into the main flow; the rest returns in later phases:

| Feature | Status | File |
|---------|--------|------|
| Logging system | ✅ Wired | `src/session/log.py` |
| App launching (sync path) | ✅ Wired | `src/app/controller.py` |
| Session Snapshots | ✅ Wired | `src/session/snapshot.py` |
| Window state persistence | ✅ Wired | `src/session/snapshot.py` |
| Config Hot Reload | ❌ Removed (manual `--reload` only) | deleted `src/config/watcher.py` |
| Time-based auto-switching | ❌ Removed (unwired) | deleted `src/session/scheduler.py` |
| Theme support | ❌ Removed (unwired) | deleted `src/ui/theme.py` |
| Desktop notifications | ✅ Wired (mode applied / not found) | `src/session/notify.py` |
| Plugin system | ✅ Wired (discovery + apply hooks) | `src/plugins/system.py` |

Async `launch_apps_async` exists but `apply_mode` uses the sync path.

---

## Linux Desktop Compatibility Initiative

A comprehensive technical plan has been developed to transition SessionIntent beyond GNOME/Wayland to support multiple Linux desktop environments. See [LINUX_DESKTOP_COMPATIBILITY_PLAN.md](../LINUX_DESKTOP_COMPATIBILITY_PLAN.md) for detailed architecture.

### Key Components
- **Provider Pattern**: Abstract display, workspace, and extension layers
- **Universal Workspace Manager**: EWMH + wlroots support
- **Session Detection**: Auto-detect desktop environment at runtime (XDG-compliant)
- **Testing Matrix**: Multi-DE/distribution validation
- **Subprocess-Based**: No new Python dependencies - uses existing system tools

### Priority Rollout
1. **Phase 1**: Foundation - XDG paths, detection system, TUI fallback
2. **Phase 2**: KDE Plasma + Hyprland (primary targets)
3. **Phase 3**: wlroots generic + Sway
4. **Phase 4**: EWMH fallback + testing

---

## Desktop Environment Support

### Current State
- **GNOME Wayland**: Supported (`gnome` workspace/extension providers)
- **KDE Plasma**: Supported (`kde` workspace via qdbus; applet listing via kpackagetool, enable/disable is manual)
- **Hyprland**: Supported (`hyprland` workspace via hyprctl)
- **Sway**: Supported (`sway` workspace via swaymsg)
- **Generic wlroots** (River, Labwc, …): Best-effort chain (hyprctl → swaymsg → EWMH)
- **Generic X11**: EWMH fallback (`wmctrl`/`xdotool`)
- Override with `sessionintent --backend <name>`; auto-detected otherwise

### Planned: KDE Plasma Support
**Difficulty**: High

Add abstraction layer for KDE Plasma workspace management:

```python
# Proposed structure
class WorkspaceManager(ABC):
    @abstractmethod
    def switch_workspace(self, num: int) -> bool: ...
    @abstractmethod
    def get_current_workspace(self) -> int | None: ...

class GNOMEWorkspaceManager(WorkspaceManager):
    # Current implementation

class KDEWorkspaceManager(WorkspaceManager):
    # Use qdbus or ... for workspace control
```

**Relevant files to modify**:
- `src/workspace/manager.py`
- `src/session/manager.py`

### Planned: Hyprland Support
**Difficulty**: Medium

Use Hyprland's IPC socket for workspace control:

```python
# Possible approach
hyprctl workspace <n>
hyprctl activeworkspace
```

### Planned: Sway Support
**Difficulty**: Medium

Use swaymsg similar to Hyprland approach.

---

## Packaging

### AUR Package (Arch Linux)
**Difficulty**: Low

Create PKGBUILD for Arch User Repository.

### Flatpak
**Difficulty**: Medium

Package as Flatpak for universal Linux distribution.

### Debian/Ubuntu Packages
**Difficulty**: Low

Create .deb package for Debian-based distributions.

---

## UI/UX Improvements

### TUI Mode
**Difficulty**: Low

Add terminal-based mode selector for headless environments:

```bash
sessionintent --tui
```

### Mode Preview
**Status**: Done

Show what apps will launch before confirming:

```bash
sessionintent preview work
# Output:
# Preview: work (Work)
#   Workspace 1: firefox, vscode
#   Workspace 2: discord (background: True)
```

---

## Testing

### CI/CD Improvements
- Add more unit tests
- Add integration tests
- Test on multiple GNOME versions

---

## How to Contribute

1. Fork the repository
2. Pick an item from this roadmap
3. Open a discussion issue before starting major work
4. Submit a pull request

For questions, reach out via GitHub Issues.