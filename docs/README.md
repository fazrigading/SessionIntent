# SessionIntent Documentation

This folder contains comprehensive documentation for SessionIntent.

## Quick Start

1. **Installation**: See `INSTALLATION.md`
2. **Configuration**: See `CONFIGURATION-GUIDE.md`
3. **Modes**: See `MODES.md`
4. **FAQ**: See `FAQ.md`

## Documentation Structure

| File | Description |
| ---- | ----------- |
| `README.md` | Overview and quick start |
| `ARCHITECTURE.md` | System architecture details |
| `CONFIGURATION-GUIDE.md` | Config file tutorial |
| `FAQ.md` | Common questions and answers |
| `INSTALLATION.md` | Installation instructions for all distros |
| `MODES.md` | Mode examples and patterns |
| `MIGRATION.md` | Subcommand CLI and `version: 2` migration guide |
| `ROADMAP.md` | Future enhancements and contribution ideas |

## For Developers

- `ARCHITECTURE.md` - Technical architecture overview
- `ROADMAP.md` - Future enhancements and contribution ideas

## Getting Help

1. Check **FAQ.md** first
2. Review **CONFIGURATION-GUIDE.md** for setup issues
3. Check existing **Issues** on GitHub
4. Open a new **Issue** with your config and steps

## Document Conventions

- **Bold** = Important
- *Italic* = Emphasis
- `code` = Code/command
- `[brackets]` = Optional
- `{braces}` = Required value

## CLI Reference

```bash
# Default: Select mode via UI
sessionintent
sessionintent select

# Apply mode
sessionintent apply MODE

# Session control
sessionintent panic    # Clear state (no app termination)
sessionintent quit     # Gracefully close apps
sessionintent clear    # Clear state files only
sessionintent kill     # Force kill apps
sessionintent suspend  # Suspend session

# Info commands
sessionintent status   # Show current status
sessionintent list     # List available modes

# Configuration
sessionintent init     # Initialize default configs and extension
sessionintent setup    # Set up SessionIntent (scan apps)
sessionintent scan     # Rescan installed apps
sessionintent reload   # Reload configuration
sessionintent version  # Display version information

# Global flags (come before the command)
sessionintent --config PATH list
sessionintent --dev apply MODE   # Dry-run mode
sessionintent --backend NAME apply MODE
```

Full flag-to-command table: [MIGRATION.md](MIGRATION.md).
