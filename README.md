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

#### Method 1: Using installer script

```bash
curl -fsSL https://raw.githubusercontent.com/fazrigading/SessionIntent/master/INSTALL.sh | bash
```

#### Method 2: Manual installation 
```bash
pip install -r requirements.txt
```

Read [docs/INSTALLATION.md](docs/INSTALLATION.md) for more details on manual installation.

### Configuration

1. Initialize SessionIntent:
```bash
sessionintent --init
```

2. Set up your apps:
```bash
sessionintent --setup
```

3. Edit `~/.config/sessionintent/config.yaml` to define your modes, read [examples/config.example.yaml](examples/config.example.yaml) for reference.

3. Launch the mode selector:
```bash
sessionintent
```

## Usage

```bash
# Select mode via UI (requires wofi/rofi) - default behavior
sessionintent

# Apply specific mode directly (without wofi/rofi)
sessionintent --mode / -m browsing

# Session control
sessionintent --panic / -P       # Clear state (no app termination)
sessionintent --quit / -q        # Gracefully close managed apps
sessionintent --clear            # Clear state files only
sessionintent --kill / -k        # Force kill managed apps
sessionintent --suspend -S       # Suspend session

# Status and listing
sessionintent --status / -s      # Show current status
sessionintent --list / -l        # List available modes

# Configuration
sessionintent --init / -i      # Initialize default configs and extension
sessionintent --setup          # Set up SessionIntent (scan apps)
sessionintent --scan-apps      # Rescan installed apps
sessionintent --reload  / -r         # Reload configuration

# Dry-run mode (for dev testing)
sessionintent --dev --mode work
sessionintent -d -m work
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
