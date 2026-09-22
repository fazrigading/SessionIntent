# SessionIntent - Declarative session orchestration for Linux desktops

SessionIntent switches between intent-based modes (work, gaming, browsing, …) that automatically launch, reuse, and organize applications across workspaces.

Backends are auto-detected: GNOME, KDE Plasma, Hyprland, Sway, generic wlroots, and an EWMH fallback — override with `--backend`.

## Features

- 🎯 **Intent-based sessions** - Define workflows as modes (work, browsing, gaming, …)
- 🖥️ **Multi-desktop** - Provider-based support for GNOME, KDE, Hyprland, Sway, wlroots, EWMH
- 🔋 **Hardware awareness** - Filter modes on battery vs AC power
- 📝 **Declarative configuration** - `config.yaml` modes + `apps.yaml` registry (`version: 2` schema)
- 🔒 **Safe by default** - Reuse before launch; destructive actions are explicit commands
- 🎛️ **Workspace orchestration** - Per-workspace app placement with optional monitor
- 👁️ **Mode preview** - `preview <mode>` shows workspaces and apps before applying
- 🔔 **Notifications** - Desktop notice on every mode switch
- 🧩 **Plugins** - Drop-in hooks in `~/.config/sessionintent/plugins/`
- 🧪 **Dev mode** - `--dev` prints commands instead of executing

## Quick Start

### Installation

#### Method 1: Using uv (recommended)

```bash
uv tool install git+https://github.com/fazrigading/SessionIntent
```

Or run without installing:

```bash
uvx --from git+https://github.com/fazrigading/SessionIntent sessionintent --help
```

#### Method 2: Using installer script

```bash
curl -fsSL https://raw.githubusercontent.com/fazrigading/SessionIntent/master/INSTALL.sh | bash
```

#### Method 3: Manual installation
```bash
pip install .
```

Read [docs/INSTALLATION.md](docs/INSTALLATION.md) for details. Distro packages: PKGBUILD in `packaging/arch/`, Debian sources in `debian/`, Flatpak manifest in `packaging/flatpak/`, RPM spec in `packaging/fedora/` (all pending upload except the installer).

### Configuration

1. Initialize SessionIntent:
```bash
sessionintent init
```

2. Set up your apps:
```bash
sessionintent setup
```

3. Edit `~/.config/sessionintent/config.yaml` to define your modes, read [examples/config.example.yaml](examples/config.example.yaml) for reference.

4. Launch the mode selector:
```bash
sessionintent
```

Upgrading from flag-based CLI or `version: 1` configs? See [docs/MIGRATION.md](docs/MIGRATION.md).

## Usage

```bash
# Select mode via UI (requires wofi/rofi) - default behavior
sessionintent
sessionintent select

# Apply specific mode directly (without wofi/rofi)
sessionintent apply browsing

# Preview a mode without applying
sessionintent preview browsing

# Session control
sessionintent panic        # Clear state (no app termination)
sessionintent quit         # Gracefully close managed apps
sessionintent clear        # Clear state files only
sessionintent kill         # Force kill managed apps
sessionintent suspend      # Suspend session

# Status and listing
sessionintent status       # Show current status
sessionintent list         # List available modes

# Configuration
sessionintent init         # Initialize default configs and extension
sessionintent setup        # Set up SessionIntent (scan apps)
sessionintent scan         # Rescan installed apps
sessionintent scan --force # Rescan, ignore cache
sessionintent reload       # Reload configuration
sessionintent version      # Display version information

# Global flags (come before the command)
sessionintent --dev apply work
sessionintent --backend sway apply work
sessionintent --config ~/other.yaml list
```

## Key Files

| File | Purpose |
| ---- | ------- |
| `~/.config/sessionintent/config.yaml` | User mode definitions (`$XDG_CONFIG_HOME` honored) |
| `~/.config/sessionintent/apps.yaml` | User app registry |
| `/usr/share/sessionintent/apps.yaml` | System app registry |
| `~/.local/state/sessionintent/current` | Current session state (`$XDG_STATE_HOME` honored) |

## Requirements

- Python 3.10+
- PyYAML
- wofi or rofi (OPTIONAL, for UI; terminal fallback otherwise)
- A supported desktop (GNOME, KDE, Hyprland, Sway, wlroots) or X11/EWMH

## License

GPL-3.0-or-later - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/ROADMAP.md](docs/ROADMAP.md) for details.

## Acknowledgments

- Provider-based multi-desktop support
- Inspired by window manager session management tools
