# SessionIntent TODO

> Rework source of truth: `plans/` (see `plans/04-phases.md`).
> This file tracks remaining user-facing work; phase status lives in `plans/README.md`.

This document tracks planned features and improvements for the SessionIntent project.

## Desktop Environment Support

### High Priority (Phase 1: Foundation)

- [ ] Implement XDG-compliant config paths in src/constants/paths.py
- [ ] Implement automated session detection system (src/session/detector.py)
- [ ] Create TUI provider as universal fallback
- [ ] Add CLI flags for manual override (--force-backend)

### High Priority (Phase 2: KDE & Hyprland)

- [ ] Refactor src/workspace/manager.py to provider pattern
- [ ] Add KDE Plasma Support - create abstraction layer with qdbus
- [ ] Add Hyprland Support - use IPC socket (hyprctl)
- [ ] Add KDE extension provider for src/extensions/manager.py

### Medium Priority (Phase 3: wlroots & Sway)

- [ ] Add generic Wayland provider (wlr-foreign-toplevel)
- [ ] Add Sway Support - use swaymsg
- [ ] Test on wlroots compositors (River, Labwc)

### Lower Priority (Phase 4: EWMH Fallback)

- [ ] Test and verify GNOME X11 support
- [ ] Implement EWMH fallback provider (wmctrl/xdotool)
- [ ] Create comprehensive testing matrix for multi-DE support

### Technical Plan
See LINUX_DESKTOP_COMPATIBILITY_PLAN.md for detailed implementation roadmap.

### Notes
Ref: docs/ROADMAP.md, LINUX_DESKTOP_COMPATIBILITY_PLAN.md

## Core Features

### High Priority

- [x] Add logging system
- [x] Session Snapshots - save and restore window positions
- [x] Window state persistence
- [ ] Config Hot Reload - removed in Phase 1 (manual `--reload` only, see `plans/`)
- [ ] Time-based auto-switching - removed in Phase 1 (unwired, see `plans/`)
- [ ] Desktop notifications - present but unwired (see `plans/`)
- [ ] Theme support - removed in Phase 1 (unwired, see `plans/`)

### Medium Priority

- [ ] Plugin system architecture - present but unwired (see `plans/`)

### Low Priority

- [ ] Desktop notifications - present but unwired (see above)
- [ ] Theme support - removed in Phase 1 (see above)

Ref: docs/ROADMAP.md

## Packaging

### High Priority

- [ ] Create AUR Package (PKGBUILD for Arch Linux)
- [ ] Create Debian/Ubuntu Packages (.deb)

### Medium Priority

- [ ] Package as Flatpak for universal Linux distribution

Ref: docs/ROADMAP.md

## UI/UX Improvements

### High Priority

- [ ] Add TUI Mode - terminal-based mode selector for headless
- [ ] Add Mode Preview - show apps before confirming

Ref: docs/ROADMAP.md

## Testing

### High Priority

- [ ] Add more comprehensive unit tests
- [ ] Add integration tests
- [ ] Test on multiple GNOME versions
- [ ] Automate CI/CD improvements for testing

Ref: docs/ROADMAP.md

## Code Quality

### Ongoing

- [ ] Maintain PEP 8 compliance
- [ ] Keep type hints updated
- [ ] Ensure documentation stays current
- [ ] Regular dependency updates

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/ROADMAP.md](docs/ROADMAP.md) for how to help.