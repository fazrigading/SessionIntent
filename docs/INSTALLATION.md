# Installation Guide

## Requirements

- Python 3.10+
- PyYAML
- `wofi` or `rofi` — optional, for the mode picker. Without either, SessionIntent
  falls back to a terminal menu.
- A supported DE or compositor: GNOME, KDE Plasma, Hyprland, Sway, wlroots, or
  X11/EWMH

## Quick Install

### Fedora

```bash
sudo dnf copr enable fazrigading/SessionIntent
sudo dnf install sessionintent
```

The COPR project name is case-sensitive. The RPM ships the CLI, the man page,
and the example configs, but no autostart entry — run `sessionintent init` once
after installing.

### Any distribution

Install the dependencies:

```bash
# Fedora
sudo dnf install python3-pyyaml wofi
# Debian / Ubuntu
sudo apt install python3-pip python3-yaml rofi
# Arch
sudo pacman -S python python-yaml rofi
```

Then run the installer:

```bash
curl -fsSL https://raw.githubusercontent.com/fazrigading/SessionIntent/master/INSTALL.sh | bash
```

The script checks prerequisites, installs SessionIntent with `uv` (falling back
to `pip`), seeds a default config, and sets up autostart.

### uv

If you already use [uv](https://docs.astral.sh/uv/):

```bash
uv tool install git+https://github.com/fazrigading/SessionIntent
```

Manage it with:

```bash
uv tool upgrade sessionintent
uv tool uninstall sessionintent
```

Or run it without installing:

```bash
uvx --from git+https://github.com/fazrigading/SessionIntent sessionintent --help
```

## Verify

```bash
which sessionintent                # is it on PATH?
sessionintent --help
sessionintent --dev apply browsing   # dry run, prints commands
```

## Manual Installation

To install from a clone instead of using the script:

```bash
git clone https://github.com/fazrigading/SessionIntent.git
cd SessionIntent
```

### Install the package

With uv:

```bash
uv tool install .
```

Or with pip:

```bash
pip install .
```

> [!IMPORTANT]
> Distros that mark system Python as externally managed (PEP 668 — Fedora,
> recent Debian/Ubuntu) may reject a bare `pip install .`. Use a virtualenv
> (`python3 -m venv .venv && source .venv/bin/activate`) or pipx in that case.

For an editable development environment:

```bash
uv sync
uv run sessionintent --help
```

Ensure `~/.local/bin` is on your `PATH`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Configuration

`sessionintent init` creates `~/.config/sessionintent` and seeds both config
files, leaving any existing config untouched:

```bash
sessionintent init
```

To do it by hand instead:

```bash
mkdir -p ~/.config/sessionintent ~/.local/state/sessionintent
cp examples/config.example.yaml ~/.config/sessionintent/config.yaml
cp examples/apps.example.yaml ~/.config/sessionintent/apps.yaml
```

### Autostart (optional)

The installer script sets this up for you. To do it manually:

```bash
mkdir -p ~/.config/autostart

cat > ~/.config/autostart/sessionintent.desktop << EOF
[Desktop Entry]
Type=Application
Name=SessionIntent
Comment=Session mode selector
Exec=sessionintent
X-GNOME-AutoRestart=false
X-GNOME-Autostart-Delay=3
EOF
```

## Uninstallation

### Installer script

```bash
./INSTALL.sh --uninstall
```

This removes the tool and leaves your config alone. To also remove the autostart
entry, set `CONFIRM_UNINSTALL=1`:

```bash
CONFIRM_UNINSTALL=1 ./INSTALL.sh --uninstall
```

Adding `REMOVE_CONFIG=1` additionally deletes `~/.config/sessionintent`,
which **destroys your custom config**:

```bash
CONFIRM_UNINSTALL=1 REMOVE_CONFIG=1 ./INSTALL.sh --uninstall
```

### uv

```bash
uv tool uninstall sessionintent
```

### Distro package

```bash
sudo dnf remove sessionintent    # Fedora
```

### Manually

```bash
rm -f ~/.local/bin/sessionintent
rm -f ~/.config/autostart/sessionintent.desktop
rm -rf ~/.config/sessionintent   # WARNING: deletes your custom config
```

## Troubleshooting

### `sessionintent: command not found`

Add `~/.local/bin` to your `PATH`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### `No module named 'yaml'`

```bash
sudo dnf install python3-pyyaml    # Fedora
sudo apt install python3-yaml      # Debian / Ubuntu
sudo pacman -S python-yaml         # Arch
```

### `wofi` or `rofi` not found

The mode picker needs one of them. SessionIntent otherwise falls back to a
terminal menu, so this is not fatal.

```bash
sudo dnf install wofi    # Fedora
sudo apt install rofi    # Debian / Ubuntu
sudo pacman -S rofi      # Arch
```

### Permission denied on config

```bash
ls -la ~/.config/sessionintent/
chmod 644 ~/.config/sessionintent/*.yaml
```

## Advanced Installation

### Custom install location

```bash
INSTALL_DIR="/path/to/dir" ./INSTALL.sh
```

### Skip autostart setup

```bash
INSTALL_NO_AUTOSTART=1 ./INSTALL.sh
```

## Development Environment

Contributors can set up a full dev environment with `uv` — it installs the
project in editable mode plus pytest, pytest-cov, ruff, and mypy:

```bash
git clone https://github.com/fazrigading/SessionIntent.git
cd SessionIntent
uv sync

uv run sessionintent --help
uv run pytest
```

## Contributing New Installers

We welcome installers for other distributions! See
[CONTRIBUTING.md](../CONTRIBUTING.md) for details.
