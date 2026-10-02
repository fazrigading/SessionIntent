# SessionIntent TODO

> Rework source of truth: `plans/` (see `plans/04-phases.md`).
> This file tracks remaining user-facing work; phase status lives in `plans/README.md`.

This document tracks planned features and improvements for the SessionIntent project.

## Desktop Environment Support

All provider work is shipped (`src/sessionintent/providers/`); unchecked
items below are manual verification, not implementation.

### Verification (manual, needs real hardware)

- [ ] Test on wlroots compositors (River, Labwc)
- [ ] Test and verify GNOME X11 support
- [ ] Create comprehensive testing matrix runs for multi-DE support
- [x] Test on multiple GNOME versions (50/51 verified live on Wayland, 2026-10)

### Shipped

- [x] XDG-compliant config paths
- [x] Automated session detection (`DesktopProfile` + factory)
- [x] TUI provider as universal fallback
- [x] Backend override (`--backend`)
- [x] Provider pattern + KDE (qdbus), Hyprland (hyprctl), Sway (swaymsg)
- [x] KDE extension provider (applet listing)
- [x] Generic Wayland/wlroots chain + EWMH fallback (wmctrl/xdotool)

### Technical Plan
Superseded by `plans/` (see `plans/04-phases.md`). The original
compatibility proposal is kept at `plans/00-superseded-compatibility-plan.md`.

### Notes
Ref: docs/ROADMAP.md

## Core Features

### High Priority

- [x] Add logging system
- [x] Session Snapshots - save and restore window positions
- [x] Window state persistence
- [x] Desktop notifications - wired into `apply_mode` (mode applied / not found)
- [x] TUI Mode - `TuiDisplayProvider` fallback selector (see UI/UX below)

Removed in Phase 1 (not planned work, manual alternatives noted):

- Config Hot Reload - manual `reload` only (see `plans/`)
- Time-based auto-switching - unwired, removed (see `plans/`)
- Theme support - unwired, removed (see `plans/`)

### Medium Priority

- [x] Plugin system architecture - apply/applied hooks wired into `apply_mode`

Ref: docs/ROADMAP.md

## Packaging

### High Priority

- [ ] Publish AUR Package (files: `packaging/arch/PKGBUILD`; needs checksums + upload)
- [ ] Publish Debian/Ubuntu Packages (files: `debian/`; needs upload)

### Medium Priority

- [ ] Publish Flatpak (files: `packaging/flatpak/`; needs checksum + submission)

Ref: docs/ROADMAP.md

## UI/UX Improvements

### High Priority

- [x] Add TUI Mode - terminal-based mode selector fallback
- [x] Add Mode Preview - `preview <mode>` shows apps before applying

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