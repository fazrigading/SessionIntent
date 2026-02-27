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

# Apply mode
sessionintent -m MODE
sessionintent --mode MODE

# Session control
sessionintent -P / --panic    # Clear state (no app termination)
sessionintent -q / --quit    # Gracefully close apps
sessionintent --clear        # Clear state files only
sessionintent -k / --kill    # Force kill apps
sessionintent -S / --suspend # Suspend session

# Info commands
sessionintent -s / --status  # Show current status
sessionintent -l / --list    # List available modes

# Configuration
sessionintent -i / --init    # Initialize default configs
sessionintent -r / --reload   # Reload configuration
sessionintent -c / --config   # Custom config file

# Dev mode
sessionintent -d / --dev      # Dry-run mode
```
