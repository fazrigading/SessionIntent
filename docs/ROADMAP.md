# SessionIntent Roadmap

This document outlines potential future enhancements and areas for community contribution.

## Completed Features

All Core Features from TODO.md have been implemented:

| Feature | Status | File |
|---------|--------|------|
| Logging system | ✅ Done | `src/session/log.py` |
| Async App Launching | ✅ Done | `src/app/controller.py` |
| Config Hot Reload | ✅ Done | `src/config/watcher.py` |
| Session Snapshots | ✅ Done | `src/session/snapshot.py` |
| Window state persistence | ✅ Done | `src/session/snapshot.py` |
| Plugin system | ✅ Done | `src/plugins/system.py` |
| Time-based auto-switching | ✅ Done | `src/session/scheduler.py` |
| Desktop notifications | ✅ Done | `src/session/notify.py` |
| Theme support | ✅ Done | `src/ui/theme.py` |

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
- **GNOME Wayland**: Fully supported (existing)
- **KDE Plasma**: Planned (Priority 1)
- **Hyprland**: Planned (Priority 1)
- **Generic wlroots**: Planned (Priority 2)
- **Sway**: Planned (Priority 2)
- **GNOME X11**: May work with existing gdbus

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
**Difficulty**: Medium

Show what apps will launch before confirming:

```bash
sessionintent --preview work
# Output:
# Workspace 1: firefox (profile: work), vscode
# Workspace 2: slack, thunderbird
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