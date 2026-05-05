# SessionIntent - Installation Guide

## Quick Install

### Method 1: One-liner (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/fazrigading/SessionIntent/master/INSTALL.sh | bash
```

### Method 2: Manual Installation

#### Prerequisites

Before installing SessionIntent, ensure you have:

```bash
# Python 3.10+
python3 --version

# PyYAML
pip install PyYAML

# UI tool (one of)
sudo dnf install wofi    # Fedora
sudo apt install rofi    # Ubuntu/Debian
```

#### Steps

1. **Clone the repository**
```bash
git clone https://github.com/fazrigading/SessionIntent.git
cd SessionIntent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run installer**
```bash
./INSTALL.sh
```

This will:
- Copy `sessionintent.py` to `~/.local/bin/sessionintent`
- Create config directory `~/.config/sessionintent/`
- Install default configs
- Create autostart entry

4. **Verify installation**
```bash
sessionintent --help
```

## Manual Installation

If you prefer to install manually:

### 1. Copy Script

```bash
cp sessionintent.py ~/.local/bin/sessionintent
chmod +x ~/.local/bin/sessionintent
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
cp config.yaml.example ~/.config/sessionintent/config.yaml
cp apps.yaml.example ~/.config/sessionintent/apps.yaml
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

## Installation with RPM Package (Fedora)

### Enable COPR Repository

```bash
sudo dnf copr enable fazrigading/sessionintent
sudo dnf install sessionintent
```

## Installation with Arch Linux (AUR)

Using an AUR helper:

```bash
yay -S sessionintent
# or
paru -S sessionintent
```

## Distribution-Specific Notes

### Fedora

SessionIntent is designed for Linux with GNOME Wayland.

```bash
# Install dependencies
sudo dnf install python3-pyyaml wofi gnome-shell

# Install SessionIntent
curl -fsSL https://example.com/install.sh | bash
```

### Ubuntu/Debian

```bash
# Install dependencies
sudo apt install python3-pip python3-yaml rofi

# Clone and install
git clone https://github.com/fazrigading/SessionIntent.git
cd SessionIntent
pip3 install -r requirements.txt
./INSTALL.sh
```

### Other Distributions

Use the general installation method:

```bash
pip3 install PyYAML
curl -fsSL https://example.com/install.sh | bash
```

## Verification

After installation, verify:

```bash
# Check command exists
which sessionintent

# Show help
sessionintent --help

# Test in dev mode
sessionintent --dev --mode browsing
```

## Uninstallation

### Using Script

```bash
./INSTALL.sh --uninstall
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

## Contributing New Installers

We welcome installers for other distributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
