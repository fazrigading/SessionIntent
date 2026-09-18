"""
SessionIntent CLI Argument Parser
Subcommand interface with global modifiers.
"""

from __future__ import annotations

import argparse

COMMANDS = (
    "apply",
    "preview",
    "select",
    "list",
    "status",
    "panic",
    "quit",
    "clear",
    "kill",
    "suspend",
    "init",
    "setup",
    "scan",
    "reload",
    "version",
)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="sessionintent",
        description="SessionIntent Orchestrator made by Fazri Gading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sessionintent select                          # Select mode via UI (default)
  sessionintent apply work                      # Apply 'work' mode directly
  sessionintent preview work                    # Preview 'work' mode
  sessionintent list                            # List available modes
  sessionintent status                          # Show current session status
  sessionintent scan --force                    # Rescan apps, ignore cache
  sessionintent --dev apply work                # Dry-run 'work' mode
  sessionintent --backend sway apply work       # Force Sway backend
""",
    )

    parser.add_argument(
        "-c", "--config", type=str, help="Path to custom configuration file"
    )
    parser.add_argument(
        "-d",
        "--dev",
        action="store_true",
        help="Dev mode: Print commands instead of executing",
    )
    parser.add_argument(
        "--backend",
        type=str,
        choices=["gnome", "ewmh", "kde", "hyprland", "sway", "wlroots"],
        default=None,
        help="Workspace backend override (default: auto-detect)",
    )

    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.add_parser("apply", help="Apply a specific mode").add_argument(
        "mode", help="Mode to apply"
    )
    sub.add_parser("preview", help="Preview a mode without applying").add_argument(
        "mode", help="Mode to preview"
    )
    sub.add_parser("select", help="Select mode via UI (default)")
    sub.add_parser("list", help="List available modes")
    sub.add_parser("status", help="Show current session status")
    sub.add_parser("panic", help="Clear state without killing apps")
    sub.add_parser("quit", help="Gracefully close managed apps")
    sub.add_parser("clear", help="Clear state files only")
    sub.add_parser("kill", help="Force kill managed apps")
    sub.add_parser("suspend", help="Suspend the current session")
    sub.add_parser("init", help="Initialize default configs and extension")
    sub.add_parser("setup", help="Interactive app setup wizard")
    scan = sub.add_parser("scan", help="Rescan installed apps")
    scan.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force fresh scan, ignore cache",
    )
    scan.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable cache usage for app detection",
    )
    scan.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the cached app detection results",
    )
    sub.add_parser("reload", help="Reload configuration files")
    sub.add_parser("version", help="Display version information")

    return parser


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = create_parser()
    return parser.parse_args(args)


def get_help_message() -> str:
    """Get the full help message."""
    parser = create_parser()
    return parser.format_help()
