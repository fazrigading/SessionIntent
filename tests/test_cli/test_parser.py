"""Tests for CLI argument parser."""

import pytest

from src.cli.parser import (
    create_parser,
    parse_args,
    validate_args,
    get_help_message,
)


class TestCreateParser:
    """Test parser creation."""

    def test_parser_creation(self):
        """Test that parser is created successfully."""
        parser = create_parser()
        assert parser is not None


class TestParseArgs:
    """Test argument parsing."""

    @pytest.mark.parametrize(
        "flag,value,expected",
        [
            ("--mode", "work", "work"),
            ("-m", "gaming", "gaming"),
            ("--config", "/path/to/config.yaml", "/path/to/config.yaml"),
        ],
    )
    def test_parse_args_with_values(self, flag, value, expected):
        """Test parsing arguments with values."""
        args = parse_args([flag, value])
        if flag in ("--mode", "-m"):
            assert args.mode == expected
        elif flag == "--config":
            assert args.config == expected

    @pytest.mark.parametrize(
        "flag,expected_attr",
        [
            ("--panic", "panic"),
            ("--quit", "quit"),
            ("--clear", "clear"),
            ("--init", "init"),
            ("-i", "init"),
            ("--setup", "setup"),
            ("--scan-apps", "scan_apps"),
            ("--dev", "dev"),
            ("--status", "status"),
            ("--list", "list"),
            ("--kill", "kill"),
            ("--reload", "reload"),
            ("--suspend", "suspend"),
        ],
    )
    def test_parse_boolean_flags(self, flag, expected_attr):
        """Test parsing boolean flag arguments."""
        args = parse_args([flag])
        assert getattr(args, expected_attr) is True

    def test_parse_multiple_args(self):
        """Test parsing multiple arguments together."""
        args = parse_args(["--mode", "work", "--dev", "--config", "config.yaml"])
        assert args.mode == "work"
        assert args.dev is True
        assert args.config == "config.yaml"

    def test_parse_empty_args(self):
        """Test parsing empty args returns defaults."""
        args = parse_args([])
        assert args.mode is None
        assert args.config is None
        assert args.panic is False


class TestValidateArgs:
    """Test argument validation."""

    @pytest.mark.parametrize(
        "flag",
        [
            "panic",
            "quit",
            "clear",
            "init",
            "setup",
            "scan-apps",
            "kill",
            "suspend",
            "reload",
            "status",
            "list",
        ],
    )
    def test_validate_single_action_flag(self, flag):
        """Test valid: each action flag alone."""
        args = parse_args([f"--{flag}"])
        is_valid, error = validate_args(args)
        assert is_valid is True, f"Failed for {flag}: {error}"

    def test_validate_mode_alone(self):
        """Test valid: mode alone."""
        args = parse_args(["--mode", "work"])
        is_valid, error = validate_args(args)
        assert is_valid is True

    @pytest.mark.parametrize("conflict", ["panic", "quit", "clear", "kill", "suspend"])
    def test_validate_mode_with_conflicting_args(self, conflict):
        """Test invalid: mode with conflicting args."""
        args = parse_args(["--mode", "work", f"--{conflict}"])
        is_valid, error = validate_args(args)
        assert is_valid is False
        assert "Cannot use --mode with" in error

    @pytest.mark.parametrize(
        "flags",
        [
            ["--panic", "--quit"],
            ["--panic", "--clear"],
            ["--panic", "--kill"],
        ],
    )
    def test_validate_multiple_exclusive_actions(self, flags):
        """Test invalid: multiple exclusive actions together."""
        args = parse_args(flags)
        is_valid, error = validate_args(args)
        assert is_valid is False
        assert "Only one action flag allowed" in error

    def test_validate_empty_mode(self):
        """Test valid: empty mode passes validation (argparse handles it)."""
        args = parse_args(["--mode", ""])
        is_valid, _ = validate_args(args)
        assert is_valid is True


class TestGetHelpMessage:
    """Test help message generation."""

    def test_get_help_message_returns_string(self):
        """Test that help message is returned as string."""
        msg = get_help_message()
        assert isinstance(msg, str)

    def test_help_message_contains_examples(self):
        """Test that help message contains examples."""
        msg = get_help_message()
        assert "Examples:" in msg
        assert "--mode" in msg
