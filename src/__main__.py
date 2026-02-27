#!/usr/bin/env python3
"""
SessionIntent - Session Orchestration for GNOME Wayland

Usage:
    sessionintent --prompt           # Select mode via UI
    sessionintent --mode WORKSPACE   # Apply specific mode
    sessionintent --panic            # Clear state
    sessionintent --init             # Initialize configs
    sessionintent --dev --mode M     # Dry-run mode

See 'sessionintent --help' for more information.
"""

import sys

from .cli import parse_args, validate_args, get_help_message
from .session import SessionManager


def main() -> int:
    """Main entry point for the CLI."""
    args = parse_args()

    is_valid, error = validate_args(args)
    if not is_valid:
        print(f"Error: {error}")
        print("Use --help for usage information.")
        return 1

    manager = SessionManager(dev_mode=args.dev, config_path=args.config)

    if args.init:
        manager.init_config()
    elif args.panic:
        manager.panic()
    elif args.mode:
        manager.apply_mode(args.mode)
    elif args.prompt:
        mode = manager.select_mode()
        if mode:
            manager.apply_mode(mode)
    else:
        print(get_help_message())

    return 0


if __name__ == "__main__":
    sys.exit(main())
