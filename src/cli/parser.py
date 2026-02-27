"""
SessionIntent CLI Argument Parser
Sets up and parses command-line arguments for the session orchestrator.
"""

from __future__ import annotations

import argparse


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="SessionIntent Orchestrator made by Fazri Gading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sessionintent                                   # Select mode via UI
  sessionintent [-i / --init]                     # Initialize default configs
  sessionintent [-m / --mode] work                # Apply 'work' mode directly
  sessionintent [-P / --panic]                    # Clear state (no app termination)
  sessionintent [-q / --quit]                     # Close managed applications
  sessionintent --clear                           # Clear state files only
  sessionintent [-k / --kill]                    # Force kill managed applications
  sessionintent [-s / --status]                   # Show current status
  sessionintent [-l / --list]                     # List available modes
  sessionintent [-r / --reload]                   # Reload configuration
  sessionintent [-S / --suspend]                  # Suspend session
  sessionintent [-d / --dev] [-m / --mode] work  # Simulate 'work' mode
  sessionintent [-h]                              # Show command usage / help
""",
    )

    parser.add_argument(
        "-m", "--mode", type=str, help="Apply a specific mode (bypasses UI selector)"
    )

    parser.add_argument(
        "-c", "--config", type=str, help="Path to custom configuration file"
    )

    parser.add_argument(
        "-P",
        "--panic",
        action="store_true",
        help="Clear current session state (without killing apps)",
    )

    parser.add_argument(
        "-q",
        "--quit",
        action="store_true",
        help="Gracefully close managed applications",
    )

    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear state files only (without touching apps)",
    )

    parser.add_argument(
        "-i",
        "--init",
        action="store_true",
        help="Initialize default configuration files",
    )

    parser.add_argument(
        "-d",
        "--dev",
        action="store_true",
        help="Dev mode: Print commands instead of executing",
    )

    parser.add_argument(
        "-s",
        "--status",
        action="store_true",
        help="Show current session status",
    )

    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List available modes",
    )

    parser.add_argument(
        "-k",
        "--kill",
        action="store_true",
        help="Force kill managed applications (SIGKILL)",
    )

    parser.add_argument(
        "-r",
        "--reload",
        action="store_true",
        help="Reload configuration files",
    )

    parser.add_argument(
        "-S",
        "--suspend",
        action="store_true",
        help="Suspend session (pause mode switching)",
    )

    parser.add_argument(
        "--version", action="store_true", help="Display version information"
    )

    return parser


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = create_parser()
    return parser.parse_args(args)


def validate_args(args: argparse.Namespace) -> tuple:
    """
    Validate argument combinations and return error message if invalid.

    Returns:
        Tuple of (is_valid, error_message)
    """
    exclusive_actions = [
        args.mode is not None,
        args.panic,
        args.quit,
        args.clear,
        args.init,
        args.kill,
        args.suspend,
    ]

    conflicting_actions = [
        args.panic,
        args.quit,
        args.clear,
        args.kill,
        args.suspend,
    ]

    if args.mode is not None and sum(conflicting_actions) > 0:
        return (
            False,
            "Cannot use --mode with --panic, --quit, --clear, --kill, or --suspend",
        )

    if sum(exclusive_actions) > 1:
        return False, "Only one action flag allowed at a time"

    if args.mode and not args.mode.strip():
        return False, "Mode name cannot be empty"

    return True, None


def get_help_message() -> str:
    """Get the full help message."""
    parser = create_parser()
    return parser.format_help()
