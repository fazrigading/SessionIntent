# SessionIntent - Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2026-05-08

### Added
- `--init` (`-i`) flag for initializing SessionIntent (extension + defaults)
- `--setup` flag for interactive setup wizard (scan apps)

### Changed
- Split init and setup into separate commands:
  - `--init` (`-i`): Install extension and create default configs
  - `--setup`: Scan and select apps
- Added `-i` alias for `--init`

## [0.3.0] - 2026-05-06

### Added
- `--setup` flag for interactive setup wizard
- `--scan-apps` flag for rescan/rescan options
- App detection system from multiple sources (flatpak, .desktop, dpkg, rpm)
- Categorized app output in apps.yaml
- First-run automatic prompt for setup
- Interactive category and app selection

### Changed
- Replaced `--init` with `--setup` for more descriptive setup process
- Apps now scanned and detected from system

## [0.2.0] - 2026-02-24

### Added
- Dev mode for dry-run testing
- Hardware-aware mode switching
- Panic reset command
- Separate session control commands:
  - `--quit` (-q): Gracefully close managed applications (SIGTERM)
  - `--clear`: Clear state files only (no app management)
  - `--kill` (-k): Force kill managed applications (SIGKILL)
  - `--suspend` (-S): Suspend session (pause mode switching)
- Status and listing commands:
  - `--status` (-s): Show current session status
  - `--list` (-l): List available modes
  - `--reload` (-r): Reload configuration files
- Short flags for existing options:
  - `-m` / `--mode`
  - `-c` / `--config`
  - `-P` / `--panic`
  - `-i` / `--init`
  - `-d` / `--dev`
- YAML configuration support
- GNOME workspace switching
- Application launch/reuse system
- Device mode for testing

### Removed
- Default behavior: `--prompt` is now the default when no arguments provided

## [0.1.0] - 2026-02-20

### Added
- Initial release with core functionality
- Project planning and documentation
- Architecture design
- Initial implementation plan