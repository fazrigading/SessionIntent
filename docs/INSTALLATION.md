# SessionIntent - Installation Guide

## Quick Install

### Method 1: Using installer script (Recommended)

```bash
# Fedora-based
sudo dnf install python3-pyyaml gnome-shell wofi
# Debian-based
sudo apt install python3-pip python3-yaml rofi
# Arch-based
sudo pacman -S python python-yaml rofi
```

Note: `wofi` or `rofi` for UI selector (recommended to install)

```bash
curl -fsSL https://raw.githubusercontent.com/fazrigading/SessionIntent/master/INSTALL.sh | bash
```

### Method 2: uv

Install [uv](https://docs.astral.sh/uv/), then:

```bash
uv tool install git+https://github.com/fazrigading/SessionIntent
```

Manage the installation:

```bash
uv tool upgrade sessionintent
uv tool uninstall sessionintent
```

Or run without installing:

```bash
uvx --from git+https://github.com/fazrigading/SessionIntent sessionintent --help
```

uv is a supported convenience layer; pip remains fully supported (see Manual Installation below).


## Installation with RPM Package (Fedora)

Published to COPR. The project name is case-sensitive.

```bash
sudo dnf copr enable fazrigading/SessionIntent
sudo dnf install sessionintent
```

Available from the next tagged release. The RPM ships the CLI, the man page,
and the example configs; it does **not** install an autostart entry, so run
`sessionintent init` once after installing.

## Distribution-Specific Notes

### Fedora

SessionIntent supports GNOME, KDE, Hyprland, Sway, wlroots, and EWMH (auto-detected).

```bash
# Install dependencies (GNOME/Wayland example)
sudo dnf install python3-pyyaml wofi gnome-shell

# Install SessionIntent
curl -fsSL https://raw.githubusercontent.com/fazrigading/SessionIntent/master/INSTALL.sh | bash
```

### Ubuntu/Debian

```bash
# Install dependencies
sudo apt install python3-pip python3-yaml rofi

# Clone and install
git clone https://github.com/fazrigading/SessionIntent.git
cd SessionIntent
pip3 install .
./INSTALL.sh
```

### Arch Linux

```bash
# Install dependencies
sudo pacman -S python python-yaml rofi

# Clone and install
git clone https://github.com/fazrigading/SessionIntent.git
cd SessionIntent
pip install .
./INSTALL.sh
```

### Other Distributions

Use the general installation method:

```bash
pip3 install PyYAML
curl -fsSL https://raw.githubusercontent.com/fazrigading/SessionIntent/master/INSTALL.sh | bash
```

## Verification

After installation, verify:

```bash
# Check command exists
which sessionintent

# Show help
sessionintent --help

# Test in dev mode
sessionintent --dev apply browsing
```

## Manual Installation

If you prefer to install manually:

### 0. Prequisites

Install `wofi` or `rofi` for UI selector (optional, nice to have):

```bash
sudo dnf install wofi    # Fedora
sudo apt install rofi    # Ubuntu/Debian
sudo pacman -S rofi      # Arch Linux
```

git clone https://github.com/fazrigading/SessionIntent.git
cd SessionIntent

### 1. Install Package

```bash
pip install .
```

> [!IMPORTANT]
> Distros that mark system Python as externally managed (PEP 668, e.g. Fedora, recent Ubuntu/Debian) **may** reject a bare `pip install .`. Use a virtual environment (`python3 -m venv .venv && source .venv/bin/activate`) or pipx in that case.

From a local clone you can also use uv:

```bash
uv tool install .
```

For an editable development environment:

Using uv:
```bash
uv sync
uv run sessionintent --help
```

Using pip:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
sessionintent --help
```

Ensure `~/.local/bin` is in your `$PATH`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Create Config Directory

```bash
mkdir -p ~/.config/sessionintent
mkdir -p ~/.local/state/sessionintent
```

### 3. Install Default Configs

```bash
# Copy example configs
cp examples/config.example.yaml ~/.config/sessionintent/config.yaml
cp examples/apps.example.yaml ~/.config/sessionintent/apps.yaml
```

### 4. Set Up Autostart (Optional)

Create desktop file:

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

### Using Script

```bash
./INSTALL.sh --uninstall
```

### uv

```bash
uv tool uninstall sessionintent
```

### Manual

```bash
# Remove script
rm ~/.local/bin/sessionintent

# Remove configs (WARNING: This deletes your custom config!)
rm -rf ~/.config/sessionintent

# Remove autostart
rm ~/.config/autostart/sessionintent.desktop
```

## Troubleshooting

### "sessionintent: command not found"

Add to `$PATH`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "PyYAML not found"

Install:

```bash
pip3 install PyYAML
```

### "wofi/rofi not found"

Install one:

```bash
# Fedora
sudo dnf install wofi

# Ubuntu/Debian
sudo apt install rofi

# Arch Linux
sudo pacman -S rofi
```

### "Permission denied" on config

Check permissions:

```bash
ls -la ~/.config/sessionintent/
chmod 644 ~/.config/sessionintent/*.yaml
```

## Advanced Installation

### Custom Install Location

```bash
INSTALL_DIR="/path/to/custom/dir" ./INSTALL.sh
```

### No Autostart

```bash
INSTALL_NO_AUTOSTART=1 ./INSTALL.sh
```

### Skip Dependencies Check

```bash
SKIP_DEPS_CHECK=1 ./INSTALL.sh
```

## Development Environment

Contributors can set up a full dev environment with uv (installs the project in editable mode plus pytest, pytest-cov, ruff, and mypy):

```bash
git clone https://github.com/fazrigading/SessionIntent.git
cd SessionIntent
uv sync

uv run sessionintent --help
uv run pytest
```

## Contributing New Installers

We welcome installers for other distributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
