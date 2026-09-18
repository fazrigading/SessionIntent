#!/usr/bin/env python3
"""
SessionIntent - Session Orchestration for Linux Desktops

Usage:
    sessionintent [--config PATH] [--dev] [--backend NAME] <command> [args]

Commands:
    apply <mode>   Apply a specific mode
    preview <mode> Preview a mode without applying
    select         Select mode via UI (default when no command is given)
    list           List available modes
    status         Show current session status
    panic          Clear state (no app termination)
    quit           Gracefully close managed apps
    clear          Clear state files only
    kill           Force kill managed apps
    suspend        Suspend session
    init           Initialize default configs and extension
    setup          Interactive app setup wizard
    scan           Rescan installed apps
    reload         Reload configuration
    version        Display version information

See 'sessionintent --help' for more information.
"""

import sys

from .cli import parse_args
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


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    args = parse_args(argv)
    command = args.command or "select"

    if command == "version":
        from . import __version__

        print(f"sessionintent {__version__}")
        return 0

    if command == "scan" and args.clear_cache:
        from .app.cache import invalidate_cache

        if invalidate_cache():
            print("App cache cleared successfully.")
        else:
            print("Failed to clear app cache.")
        return 0

    if command == "setup":
        from .app.setup import setup_interactive

        setup_interactive()
        return 0

    if command == "scan":
        from .app.setup import rescan_options

        rescan_options(use_cache=not (args.no_cache or args.force))
        return 0

    if command == "init":
        manager = SessionManager(
            dev_mode=args.dev, config_path=args.config, backend=args.backend
        )
        manager.init_config()
        print("Extension installation complete. Restart GNOME Shell to activate it.")
        return 0

    if check_first_run():
        prompt_first_run()

    manager = SessionManager(
        dev_mode=args.dev, config_path=args.config, backend=args.backend
    )

    if command == "reload":
        manager.reload()
    elif command == "panic":
        manager.panic()
    elif command == "quit":
        manager.quit()
    elif command == "clear":
        manager.clear()
    elif command == "kill":
        manager.kill()
    elif command == "suspend":
        manager.suspend()
    elif command == "status":
        manager.status()
    elif command == "list":
        manager.list_modes()
    elif command == "apply":
        manager.apply_mode(args.mode)
    elif command == "preview":
        manager.preview_mode(args.mode)
    else:  # select
        mode = manager.select_mode()
        if mode:
            manager.apply_mode(mode)

    return 0


if __name__ == "__main__":
    sys.exit(main())
