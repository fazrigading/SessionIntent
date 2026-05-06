#!/usr/bin/env python3
"""
SessionIntent - Session Orchestration for GNOME Wayland

Usage:
    sessionintent                     # Select mode via UI
    sessionintent --setup             # Set up SessionIntent
    sessionintent --mode <mode>       # Apply specific mode
    sessionintent --panic             # Clear state (no app termination)
    sessionintent --quit              # Gracefully close managed apps
    sessionintent --clear             # Clear state files only
    sessionintent --kill              # Force kill managed apps
    sessionintent --status            # Show current status
    sessionintent --list              # List available modes
    sessionintent --reload            # Reload configuration
    sessionintent --suspend           # Suspend session 
    sessionintent --scan-apps         # Rescan installed apps
    sessionintent --dev --mode <mode> # Enable dev mode

See 'sessionintent --help' for more information.
"""

import sys

from .cli import parse_args, validate_args
from .constants import CONFIG_PATH, APPS_PATH
from .session import SessionManager


def check_first_run() -> bool:
    """Check if this is the first run (no config files exist)."""
    return not CONFIG_PATH.exists() and not APPS_PATH.exists()


def prompt_first_run() -> None:
    """Prompt user to set up on first run."""
    response = input(
        "No configuration found. Would you like to set up SessionIntent? [Y/n]: "
    ).strip().lower()
    if response in ("y", "yes", ""):
        from .app.setup import setup_interactive

        setup_interactive()


def main() -> int:
    """Main entry point for the CLI."""
    args = parse_args()

    is_valid, error = validate_args(args)
    if not is_valid:
        print(f"Error: {error}")
        print("Use --help for usage information.")
        return 1

    if args.setup:
        from .app.setup import setup_interactive

        setup_interactive()
        return 0

    if args.scan_apps:
        from .app.setup import rescan_options

        rescan_options()
        return 0

    if check_first_run():
        prompt_first_run()

    manager = SessionManager(dev_mode=args.dev, config_path=args.config)

    if args.reload:
        manager.reload()
        if args.status:
            manager.status()
        if args.list:
            manager.list_modes()
    elif args.panic:
        manager.panic()
    elif args.quit:
        manager.quit()
    elif args.clear:
        manager.clear()
    elif args.kill:
        manager.kill()
    elif args.suspend:
        manager.suspend()
    elif args.status:
        manager.status()
        if args.list:
            manager.list_modes()
    elif args.list:
        manager.list_modes()
    elif args.mode:
        manager.apply_mode(args.mode)
    else:
        mode = manager.select_mode()
        if mode:
            manager.apply_mode(mode)

    return 0


if __name__ == "__main__":
    sys.exit(main())
