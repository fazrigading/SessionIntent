<div align="center">
    <h1>SessionIntent</h1>
    <b>A declarative session orchestration for Linux desktops</b><br>
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
- wofi or rofi (OPTIONAL, for UI; terminal fallback otherwise)
- A supported DE (GNOME, KDE, Hyprland, Sway, wlroots) or X11/EWMH

### Installation

<details>
<summary>Fedora Derivatives</summary>

```bash
sudo dnf copr enable fazrigading/SessionIntent
sudo dnf install sessionintent
```
    
</details>

<details>
<summary>Debian/Ubuntu Derivatives</summary>

No distro package yet. Use the installer script or `uv` below.

```bash
sudo apt install python3-pip python3-yaml rofi
```

</details>


<details>
<summary>Arch Derivatives</summary>

No distro package yet. Use the installer script or `uv` below.

```bash
sudo pacman -S python python-yaml rofi
```

</details>

#### Method 1: Using installer script (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/fazrigading/SessionIntent/master/INSTALL.sh | bash
```

#### Method 2: Using uv

```bash
uv tool install git+https://github.com/fazrigading/SessionIntent
# To run without installing:
uvx --from git+https://github.com/fazrigading/SessionIntent sessionintent --help
```

#### More Installation Methods

**Read [docs/INSTALLATION.md](docs/INSTALLATION.md) for manual install guide, how-to uninstall, custom install location, and other advanced settings.**

Distro packaging: the RPM spec in `packaging/fedora/` is the maintained one and publishes to COPR. `packaging/arch/`, `debian/`, and `packaging/flatpak/` are kept as reference for downstream packagers but are not built or published.

### Configuration

1. Initialize SessionIntent first:
```bash
sessionintent init
```

2. Set up your apps:
```bash
sessionintent setup
```

The selected apps will be saved at `~/.config/sessionintent/apps.yaml`

3. To define your modes, edit the `config.yaml` at:
```bash
~/.config/sessionintent/config.yaml
```

Read [examples/config.example.yaml](examples/config.example.yaml) for reference.

4. Launch the mode:
```bash
# UI Selector (wofi/rofi required):
sessionintent
# Without UI:
sessionintent apply <mode_name>
```

> [!WARNING]
> Upgrading from flag-based CLI or `version: 1` configs? 
> 
> Read [docs/MIGRATION.md](docs/MIGRATION.md).

> [!NOTE]
> Backends are auto-detected: GNOME, KDE Plasma, Hyprland, Sway, generic wlroots, and an EWMH fallback (override with `--backend`).

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

- Provider-based multi-desktop support
- Inspired by window manager session management tools
