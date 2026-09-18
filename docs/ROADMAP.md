# SessionIntent Roadmap

This document outlines potential future enhancements and areas for community contribution.

## Stabilized Baseline (Phase 1)

The rework plan lives in `plans/` (see `plans/04-phases.md`). Phase 1 keeps
only what is wired into the main flow; the rest returns in later phases:

| Feature | Status | File |
|---------|--------|------|
| Logging system | ✅ Wired | `src/sessionintent/session/log.py` |
| App launching (sync path) | ✅ Wired | `src/sessionintent/app/controller.py` |
| Session Snapshots | ✅ Wired | `src/sessionintent/session/snapshot.py` |
| Window state persistence | ✅ Wired | `src/sessionintent/session/snapshot.py` |
| Config Hot Reload | ❌ Removed (manual `reload` only) | deleted `src/sessionintent/config/watcher.py` |
| Time-based auto-switching | ❌ Removed (unwired) | deleted `src/sessionintent/session/scheduler.py` |
| Theme support | ❌ Removed (unwired) | deleted `src/sessionintent/ui/theme.py` |
| Desktop notifications | ✅ Wired (mode applied / not found) | `src/sessionintent/session/notify.py` |
| Plugin system | ✅ Wired (discovery + apply hooks) | `src/sessionintent/plugins/system.py` |
| Mode preview | ✅ Wired (`preview <mode>`) | `SessionManager.preview_mode` |

Async `launch_apps_async` exists but `apply_mode` uses the sync path.

---

## Linux Desktop Compatibility Initiative

A comprehensive technical plan has been developed to transition SessionIntent beyond GNOME/Wayland to support multiple Linux desktop environments. See [plans/08-desktop-compatibility.md](../plans/08-desktop-compatibility.md) for the as-built record (the original proposal is kept at `plans/00-superseded-compatibility-plan.md`).

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

### Shipped: KDE Plasma Support

KDE Plasma workspace management via `qdbus org.kde.KWin`, plus applet
listing via `kpackagetool` (enable/disable is a documented manual step).
Lives in `src/sessionintent/providers/workspace/kde.py` and
`src/sessionintent/providers/extensions/kde.py`.

### Shipped: Hyprland Support

Workspace control via `hyprctl` (`dispatch workspace`, JSON queries).
Lives in `src/sessionintent/providers/workspace/hyprland.py`.

### Shipped: Sway Support

Workspace control via `swaymsg`, plus a best-effort wlroots chain
(hyprctl → swaymsg → EWMH) for River, Labwc, and friends.
Lives in `src/sessionintent/providers/workspace/sway.py` and `wlroots.py`.

---

## Packaging

### AUR Package (Arch Linux)
**Status**: PKGBUILD in `packaging/arch/` (needs `updpkgsums` on release + AUR upload).

### Flatpak
**Status**: Manifest in `packaging/flatpak/` (needs checksum fill + Flathub submission).
Sandbox note: host process control needs `flatpak-spawn` support, not yet implemented.

### Debian/Ubuntu Packages
**Status**: Native source package in `debian/` (needs Salsa/PPA upload).

---

## UI/UX Improvements

### TUI Mode
**Status**: Done

Terminal fallback ships as `TuiDisplayProvider`: used automatically when
neither `wofi` nor `rofi` is found.

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