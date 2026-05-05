# SessionIntent TODO

This document tracks planned features and improvements for the SessionIntent project.

## Desktop Environment Support

### High Priority

- [ ] Test and verify GNOME X11 support
- [ ] Add KDE Plasma Support - create abstraction layer with qdbus
- [ ] Add Hyprland Support - use IPC socket (hyprctl)
- [ ] Add Sway Support - use swaymsg

### Notes
Ref: docs/ROADMAP.md

## Core Features

### High Priority

- [x] Add logging system
- [x] Implement Async App Launching - parallel app launching with asyncio
- [x] Implement Config Hot Reload - watch config files for changes
- [x] Implement Session Snapshots - save and restore window positions

### Medium Priority

- [x] Window state persistence
- [x] Plugin system architecture

### Low Priority

- [x] Time-based auto-switching
- [x] Desktop notifications
- [x] Theme support

Ref: docs/ROADMAP.md, PROJECT_SUMMARY.md

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