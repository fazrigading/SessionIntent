"""
SessionIntent CLI Argument Parser
Sets up and parses command-line arguments for the session orchestrator.
"""

from __future__ import annotations

import argparse


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="SessionIntent Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sessionintent --prompt           # Select mode via UI
  sessionintent --mode work        # Apply 'work' mode directly
  sessionintent --dev --mode work  # Simulate 'work' mode
  sessionintent --panic            # Clear current state
  sessionintent --init             # Initialize default configs
""",
    )

    parser.add_argument(
        "--prompt", action="store_true", help="Prompt for mode selection via UI"
    )

    parser.add_argument(
        "--mode", type=str, help="Apply a specific mode (bypasses UI selector)"
    )

    parser.add_argument("--config", type=str, help="Path to custom configuration file")

    parser.add_argument(
        "--panic", action="store_true", help="Clear current session state"
    )

    parser.add_argument(
        "--init", action="store_true", help="Initialize default configuration files"
    )

    parser.add_argument(
        "--dev",
        action="store_true",
        help="Dev mode: Print commands instead of executing",
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
    # Check for conflicting flags
    flags_used = sum([args.prompt, args.mode is not None, args.panic, args.init])

    if flags_used > 1:
        return False, "Only one mode selection flag allowed at a time"

    # Validate mode parameter
    if args.mode and not args.mode.strip():
        return False, "Mode name cannot be empty"

    return True, None


def get_help_message() -> str:
    """Get the full help message."""
    parser = create_parser()
    return parser.format_help()
