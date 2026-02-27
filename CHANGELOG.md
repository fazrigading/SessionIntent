# SessionIntent - Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- Default behavior: `--prompt` is now the default when no arguments provided

### Changed
- Improved template resolution
- Better error handling

### Deprecated
- None

### Removed
- `--prompt` flag (now default behavior)

### Fixed
- None

### Security
- None

## [0.2.0] - 2026-02-24

### Added
- Initial release with core functionality
- CLI interface with --prompt, --mode, --panic, --init flags
- YAML configuration support
- GNOME workspace switching
- Application launch/reuse system
- Device mode for testing

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

## [0.1.0] - 2026-02-20

### Added
- Project planning and documentation
- Architecture design
- Initial implementation plan

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None
