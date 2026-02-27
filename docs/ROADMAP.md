# SessionIntent Roadmap

This document outlines potential future enhancements and areas for community contribution.

## Desktop Environment Support

### Current State
- **GNOME Wayland**: Fully supported
- **GNOME X11**: Not tested (may work with modifications)

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
    # Use qdbus or k什ML for workspace control
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

## Features

### Async App Launching
**Difficulty**: Medium

Launch applications in parallel instead of sequentially:

```python
async def apply_mode_async(mode: dict):
    tasks = [launch_app(app) for app in apps]
    await asyncio.gather(*tasks)
```

### Config Hot Reload
**Difficulty**: Low

Reload config without restarting:

```python
# Watch config files for changes
inotifywait -m ~/.config/sessionintent/
```

### Session Snapshots
**Difficulty**: High

Save and restore window positions:

```python
# Use wmctrl or xdotool for X11
# Use GNOME's window search for Wayland
```

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
sessionintent --prompt --tui
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
