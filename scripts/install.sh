#!/bin/bash
# SessionIntent Installation Script
# This script installs SessionIntent and its dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"
CONFIG_DIR="$HOME/.config/sessionintent"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/sessionintent"
AUTOSTART_DIR="$HOME/.config/autostart"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        log_info "Install with: sudo dnf install python3"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))')
    log_success "Python $PYTHON_VERSION found"
    
    # Check PyYAML
    if ! python3 -c 'import yaml' 2> /dev/null; then
        log_info "Installing PyYAML..."
        if command -v pip3 &> /dev/null; then
            pip3 install PyYAML
        elif command -v pip &> /dev/null; then
            pip install PyYAML
        else
            log_error "pip not found. Please install pip or PyYAML manually"
            exit 1
        fi
    fi
    
    # Check UI tool
    if ! command -v wofi &> /dev/null && ! command -v rofi &> /dev/null; then
        log_warn "No UI tool found (wofi or rofi)"
        log_info "Install one for mode selection:"
        log_info "  Fedora: sudo dnf install wofi"
        log_info "  Ubuntu: sudo apt install rofi"
    else
        if command -v wofi &> /dev/null; then
            log_success "wofi found"
        elif command -v rofi &> /dev/null; then
            log_success "rofi found"
        fi
    fi
    
    log_success "All prerequisites met"
}

# Create directories
create_directories() {
    log_info "Creating directories..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$STATE_DIR"
    
    log_success "Directories created"
}

# Install script
install_script() {
    log_info "Installing SessionIntent..."
    
    # Check if running in dev mode
    if [ -f "$PROJECT_DIR/sessionintent.py" ]; then
        cp "$PROJECT_DIR/sessionintent.py" "$INSTALL_DIR/sessionintent"
        chmod +x "$INSTALL_DIR/sessionintent"
    else
        # If installed via pip, executable should already be in PATH
        # or we copy from a known location
        if command -v sessionintent &> /dev/null; then
            log_warn "sessionintent already installed"
            return 0
        fi
    fi
    
    log_success "SessionIntent installed to $INSTALL_DIR/sessionintent"
}

# Install configs
install_configs() {
    log_info "Installing default configurations..."
    
    # Check if config already exists
    if [ -f "$CONFIG_DIR/config.yaml" ]; then
        log_warn "Config already exists, skipping..."
    else
        if [ -f "$PROJECT_DIR/config.yaml.example" ]; then
            cp "$PROJECT_DIR/config.yaml.example" "$CONFIG_DIR/config.yaml"
        elif [ -f "$PROJECT_DIR/config.yaml" ]; then
            cp "$PROJECT_DIR/config.yaml" "$CONFIG_DIR/config.yaml"
        fi
        log_success "Config installed: $CONFIG_DIR/config.yaml"
    fi
    
    # Apps config
    if [ -f "$CONFIG_DIR/apps.yaml" ]; then
        log_warn "Apps config already exists, skipping..."
    else
        if [ -f "$PROJECT_DIR/apps.yaml.example" ]; then
            cp "$PROJECT_DIR/apps.yaml.example" "$CONFIG_DIR/apps.yaml"
        elif [ -f "$PROJECT_DIR/apps.yaml" ]; then
            cp "$PROJECT_DIR/apps.yaml" "$CONFIG_DIR/apps.yaml"
        fi
        log_success "Apps config installed: $CONFIG_DIR/apps.yaml"
    fi
}

# Install autostart entry
install_autostart() {
    if [ "${INSTALL_NO_AUTOSTART:-0}" = "1" ]; then
        log_info "Skipping autostart installation (INSTALL_NO_AUTOSTART=1)"
        return 0
    fi
    
    log_info "Setting up autostart..."
    
    mkdir -p "$AUTOSTART_DIR"
    
    cat > "$AUTOSTART_DIR/sessionintent.desktop" << EOF
[Desktop Entry]
Type=Application
Name=SessionIntent
Comment=Session mode selector
Exec=python3 $INSTALL_DIR/sessionintent --prompt
X-GNOME-AutoRestart=false
X-GNOME-Autostart-Delay=3
EOF
    
    log_success "Autostart entry installed"
}

# Setup PATH
setup_path() {
    log_info "Setting up PATH..."
    
    SHELL_CONFIG=""
    case "$SHELL" in
        */bash)
            SHELL_CONFIG="$HOME/.bashrc"
            ;;
        */zsh)
            SHELL_CONFIG="$HOME/.zshrc"
            ;;
        */fish)
            log_info "For fish shell, add: fish_add_path $INSTALL_DIR"
            return 0
            ;;
        *)
            SHELL_CONFIG="$HOME/.profile"
            ;;
    esac
    
    if ! grep -q "export PATH.*$INSTALL_DIR" "$SHELL_CONFIG" 2>/dev/null; then
        echo "" >> "$SHELL_CONFIG"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_CONFIG"
        log_success "Added to $SHELL_CONFIG"
        log_info "Reload your shell with: source $SHELL_CONFIG"
    else
        log_success "PATH already configured"
    fi
}

# Verification
verify_installation() {
    log_info "Verifying installation..."
    
    if [ -f "$INSTALL_DIR/sessionintent" ]; then
        log_success "Script exists at $INSTALL_DIR/sessionintent"
    else
        log_error "Script not found!"
        exit 1
    fi
    
    if [ -f "$CONFIG_DIR/config.yaml" ]; then
        log_success "Config exists at $CONFIG_DIR/config.yaml"
    else
        log_warn "Config not found at $CONFIG_DIR/config.yaml"
    fi
}

# Print success message
print_success_message() {
    echo ""
    log_success "SessionIntent installed successfully!"
    echo ""
    log_info "Next steps:"
    echo "  1. Reload your shell: source \$SHELL_CONFIG"
    echo "  2. Run: sessionintent --help"
    echo "  3. Configure modes in: $CONFIG_DIR/config.yaml"
    echo "  4. Select session mode: sessionintent --prompt"
    echo ""
}

# Uninstall function
uninstall() {
    log_info "Uninstalling SessionIntent..."
    
    rm -f "$INSTALL_DIR/sessionintent"
    log_success "Script removed"
    
    if [ "${CONFIRM_UNINSTALL:-0}" = "1" ]; then
        rm -f "$AUTOSTART_DIR/sessionintent.desktop"
        log_success "Autostart removed"
        
        if [ "${REMOVE_CONFIG:-0}" = "1" ]; then
            rm -rf "$CONFIG_DIR"
            log_warn "Config directory removed (all custom configs deleted!)"
        fi
    fi
    
    log_success "Uninstallation complete"
}

# Main
main() {
    log_info "SessionIntent Installation Script"
    echo "================================="
    echo ""
    
    # Handle uninstall
    if [ "${1:-}" = "--uninstall" ]; then
        uninstall
        exit 0
    fi
    
    # Handle help
    if [ "${1:-}" = "--help" ]; then
        echo "Usage: $0 [--uninstall] [--help]"
        echo ""
        echo "Options:"
        echo "  --uninstall    Uninstall SessionIntent"
        echo "  --help         Show this help"
        echo ""
        echo "Environment variables:"
        echo "  INSTALL_NO_AUTOSTART=1  Skip autostart setup"
        echo "  INSTALL_DIR=/path       Custom install location (default: ~/.local/bin)"
        echo ""
        exit 0
    fi
    
    # Run installation steps
    check_prerequisites
    create_directories
    install_script
    install_configs
    install_autostart
    setup_path
    verify_installation
    print_success_message
}

main "$@"