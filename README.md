<div align="center">
    <h1>SessionIntent</h1>
    <b>Declarative session orchestration for Linux desktops</b><br>
    <b>Describe your "intents" (modes) to orchestrate application launch, workspace layout, and session state.</b>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPL--3.0-blue.svg"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white"></a>
    <a href="https://pyyaml.org/"><img src="https://img.shields.io/badge/PyYAML-6.0%2B-blue?logo=python&logoColor=white"></a>
    <a href="https://pypi.org/project/sessionintent/"><img src="https://img.shields.io/pypi/v/sessionintent.svg?label=PyPI"></a>
    <a href="https://github.com/fazrigading/SessionIntent/actions/workflows/ci.yml"><img src="https://github.com/fazrigading/SessionIntent/actions/workflows/ci.yml/badge.svg?branch=master&label=CI"></a>
    <a href="https://github.com/fazrigading/SessionIntent/releases"><img src="https://img.shields.io/github/v/release/fazrigading/SessionIntent"></a>
    <a href="https://github.com/fazrigading/SessionIntent/stargazers"><img src="https://img.shields.io/github/stars/fazrigading/SessionIntent?style=social"></a><br>
    <a href="https://github.com/fazrigading/SessionIntent#requirements"><img src="https://img.shields.io/badge/UI-wofi%20%7C%20rofi-purple"></a>
    <a href="https://www.gnome.org/"><img src="https://img.shields.io/badge/GNOME-4A86CF?logo=gnome&logoColor=white"></a>
    <a href="https://kde.org/"><img src="https://img.shields.io/badge/KDE-1D99F3?logo=kde&logoColor=white"></a>
    <a href="https://hyprland.org/"><img src="https://img.shields.io/badge/Hyprland-00D4FF?logo=hyprland&logoColor=white"></a>
    <a href="https://swaywm.org/"><img src="https://img.shields.io/badge/Sway-68C?logo=sway&logoColor=white"></a>
    <a href="https://gitlab.freedesktop.org/wlroots/wlroots"><img src="https://img.shields.io/badge/wlroots-d69f00?logo=wayland&logoColor=white"></a>
    <a href="https://specifications.freedesktop.org/wm-spec/latest/"><img src="https://img.shields.io/badge/X11/EWMH-346f94"></a>
</div>

SessionIntent is a declarative session orchestration system for Linux desktop environments, with a focus on GNOME and Wayland. It lets you define named session modes in YAML and automatically manage applications, workspaces, and desktop state as you switch between contexts such as browsing, work, media, or focus sessions.

Instead of launching apps manually each time, you define the behavior of a session once and let SessionIntent restore it consistently.

## Features

- 🎯 **Intent-based sessions** - Define workflows as modes (work, browsing, gaming, …)
- 🖥️ **Multi-desktop** - Provider-based support for GNOME, KDE, Hyprland, Sway, wlroots, EWMH
- 🔋 **Hardware awareness** - Filter modes on battery vs AC power
- 📝 **Declarative configuration** - `config.yaml` modes + `apps.yaml` registry (`version: 2` schema)
- 🔒 **Safe by default** - Reuse before launch; destructive actions are explicit commands
- 🎛️ **Workspace orchestration** - Per-workspace app placement with optional monitor; switches wait until the app window is visible (GNOME Shell 46–51 via bundled extension)
- 👁️ **Mode preview** - `preview <mode>` shows workspaces and apps before applying
- 🔔 **Notifications** - Desktop notice on every mode switch
- 🧩 **Plugins** - Drop-in hooks in `~/.config/sessionintent/plugins/`
- 🧪 **Dev mode** - `--dev` prints commands instead of executing

## Quick Start

### Requirements

- Python 3.10+
- PyYAML
- `wofi` or `rofi` — optional, for the mode picker. Without either, SessionIntent
  falls back to a terminal menu.
- A supported DE or compositor: GNOME, KDE Plasma, Hyprland, Sway, wlroots, or
  X11/EWMH

### Installation

#### Method 1: Installer script (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/fazrigading/SessionIntent/master/INSTALL.sh | bash
```

The script checks prerequisites, installs SessionIntent, seeds a default config,
and sets up autostart.

#### Method 2: uv

```bash
uv tool install git+https://github.com/fazrigading/SessionIntent
```

To run without installing:

```bash
uvx --from git+https://github.com/fazrigading/SessionIntent sessionintent --help
```

#### Method 3: Distro packages

**Fedora:**
```bash
sudo dnf copr enable fazrigading/SessionIntent
sudo dnf install sessionintent -y
```

> [!NOTE]
> The project name is case-sensitive. The RPM **does not** set up autostart, 
> so run `sessionintent init` once after installing.

For **Debian and Arch**, there are no distro package yet. 
Install the dependencies, then use Method 1 or 2:

```bash
# Debian-based
sudo apt install python3-pip python3-yaml rofi
# Arch-based
sudo pacman -S python python-yaml rofi
```

> [!NOTE] 
> Only the Fedora RPM is built and published. `packaging/arch/`, `debian/`, 
> and `packaging/flatpak/` are kept as reference for downstream packagers.

> [!IMPORTANT]
> See [docs/INSTALLATION.md](docs/INSTALLATION.md) for manual installs,
> uninstalling, custom install locations, and troubleshooting.

### Configuration

1. Initialize SessionIntent. This writes a default config and installs the
   GNOME Shell workspace extension:

   ```bash
   sessionintent init
   ```

2. Choose the apps you want to manage:

   ```bash
   sessionintent setup
   ```

   Your selection is saved to `~/.config/sessionintent/apps.yaml`.

3. Define your modes in `~/.config/sessionintent/config.yaml`. See
   [examples/config.example.yaml](examples/config.example.yaml) for reference.

4. Launch a mode:

   ```bash
   sessionintent                    # picker (needs wofi or rofi)
   sessionintent apply browsing     # apply directly, no picker
   ```

> [!WARNING]
> Upgrading from the flag-based CLI or `version: 1` configs? See
> [docs/MIGRATION.md](docs/MIGRATION.md).

> [!NOTE]
> Backends are auto-detected: GNOME, KDE Plasma, Hyprland, Sway, generic
> wlroots, and an EWMH fallback. Override with `--backend`.

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

## License

GPL-3.0-or-later - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/ROADMAP.md](docs/ROADMAP.md) for details.

## Acknowledgments

Inspired by window manager session management tools.

## Author

Fazri Gading (Copyright 2026)