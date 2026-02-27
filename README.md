# SessionIntent - Declarative session orchestration system for Linux with GNOME Wayland

SessionIntent allows you to switch between different "intent-based modes" (Work, Gaming, Browsing, etc.) that automatically launch, reuse, and organize your applications across workspaces.

## Features

- 🎯 **Intent-based sessions** - Define your workflow as modes (work, browsing, gaming, etc.)
- 🔋 **Hardware awareness** - Automatically adjust modes based on battery/AC power
- 📝 **Declarative configuration** - Single YAML file defines everything
- 🔒 **Safe operations** - No data loss, no forced kills
- 🎛️ **Workspace orchestration** - Advisory workspace placement
- 🧪 **Dev mode** - Test configurations and system functionality
- 🔄 **Hot reload** - Edit config and apply without restart

## Quick Start

### Installation

```bash
# Method 1: Using installer script
curl -fsSL https://raw.githubusercontent.com/fazrigading/SessionIntent/master/scripts/install.sh | bash

# Method 2: Manual installation 
pip install -r requirements.txt
sessionintent --init
```

For more details on manual installation, please read (docs/INSTALLATION.md)[docs/INSTALLATION.md]

### Configuration

1. Initialize default config:
```bash
sessionintent --init
```

2. Edit `~/.config/sessionintent/config.yaml` to define your modes

3. Launch the mode selector:
```bash
sessionintent --prompt
```

### Example Config

```yaml
defaults:
  ask_before_kill: true
  reuse_workspaces: true

hardware_profiles:
  battery:
    disable_modes: [gaming]
  plugged:
    allow_all: true

modes:
  browsing:
    label: "Browsing / Chilling"
    firefox:
      profile: chill
    workspaces:
      1:
        - firefox
      2:
        - discord

  work:
    label: "Work / Research"
    firefox:
      profile: research
    workspaces:
      1:
        - firefox
        - vscode
      2:
        - terminal
```

## Usage

```bash
# Select mode via UI (requires wofi/rofi)
sessionintent --prompt

# Apply specific mode directly
sessionintent --mode browsing

# Clear current state
sessionintent --panic

# Initialize default config
sessionintent --init

# Dry-run mode (for testing)
sessionintent --dev --mode work
```

## Key Files

| File | Purpose |
| ---- | ------- |
| `~/.config/sessionintent/config.yaml` | User mode definitions |
| `~/.config/sessionintent/apps.yaml` | User app registry |
| `/usr/share/sessionintent/apps.yaml` | System app registry |
| `~/.local/state/sessionintent/current` | Current session state |

## Requirements

- Python 3.10+
- PyYAML
- wofi or rofi (OPTIONAL, for UI)
- GNOME Wayland

## Project Structure

```
SessionIntent/
├── src/
│   ├── __init__.py          # Package exports
│   ├── __main__.py          # CLI entry point
│   ├── constants/           # Configuration constants
│   │   ├── paths.py         # Directory/file paths
│   │   └── defaults.py      # Default configs
│   ├── config/              # Configuration management
│   │   ├── loader.py        # YAML loading
│   │   └── validator.py     # Schema validation
│   ├── hardware/            # Hardware detection
│   │   └── power.py         # AC/battery detection
│   ├── app/                 # Application management
│   │   ├── registry.py      # App definitions
│   │   ├── controller.py    # Launch/reuse logic
│   │   └── template.py      # Template resolution
│   ├── workspace/           # Workspace management
│   │   └── manager.py       # GNOME workspace switching
│   ├── ui/                  # User interface
│   │   ├── selector.py      # wofi/rofi interaction
│   │   └── display.py       # Menu formatting
│   ├── session/             # Session orchestration
│   │   ├── manager.py       # Main orchestrator
│   │   └── state.py         # State persistence
│   └── cli/                 # CLI
│       └── parser.py        # Argument parsing
│
└── tests/                   # Test suite
    ├── test_config/
    ├── test_hardware/
    ├── test_app/
    ├── test_workspace/
    ├── test_ui/
    └── test_session/
```

## Distribution

- **Fedora**: `sudo dnf install sessionintent` (via COPR) **[PLANNED]**
- **Other distros**: Use `install.sh` script

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/ROADMAP.md](docs/ROADMAP.md) for details.

## Acknowledgments

- Built for GNOME Wayland
- Inspired by window manager session management tools
