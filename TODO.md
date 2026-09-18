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

### Shipped

- [x] XDG-compliant config paths
- [x] Automated session detection (`DesktopProfile` + factory)
- [x] TUI provider as universal fallback
- [x] Backend override (`--backend`)
- [x] Provider pattern + KDE (qdbus), Hyprland (hyprctl), Sway (swaymsg)
- [x] KDE extension provider (applet listing)
- [x] Generic Wayland/wlroots chain + EWMH fallback (wmctrl/xdotool)

### Technical Plan
Superseded by `plans/` (see `plans/04-phases.md`). The old
`LINUX_DESKTOP_COMPATIBILITY_PLAN.md` is kept for history only.

### Notes
Ref: docs/ROADMAP.md

## Core Features

### High Priority

- [x] Add logging system
- [x] Session Snapshots - save and restore window positions
- [x] Window state persistence
- [ ] Config Hot Reload - removed in Phase 1 (manual `reload` only, see `plans/`)
- [ ] Time-based auto-switching - removed in Phase 1 (unwired, see `plans/`)
- [ ] Desktop notifications - present but unwired (see `plans/`)
- [ ] Theme support - removed in Phase 1 (unwired, see `plans/`)

### Medium Priority

- [ ] Plugin system architecture - present but unwired (see `plans/`)

### Low Priority

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