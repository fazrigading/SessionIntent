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

    def test_parser_has_all_arguments(self):
        """Test that parser has all expected arguments."""
        parser = create_parser()
        all_options = set()
        for action in parser._actions:
            all_options.update(action.option_strings)
            if not action.option_strings:
                all_options.add(action.dest)

        expected_args = [
            "-m",
            "--mode",
            "-c",
            "--config",
            "-P",
            "--panic",
            "-q",
            "--quit",
            "--clear",
            "-i",
            "--init",
            "-d",
            "--dev",
            "-s",
            "--status",
            "-l",
            "--list",
            "-k",
            "--kill",
            "-r",
            "--reload",
            "-S",
            "--suspend",
            "--version",
        ]

        for arg in expected_args:
            assert arg in all_options, f"Missing argument: {arg}"


class TestParseArgs:
    """Test argument parsing."""

    def test_parse_mode_arg(self):
        """Test parsing --mode argument."""
        args = parse_args(["--mode", "work"])
        assert args.mode == "work"

    def test_parse_mode_short_arg(self):
        """Test parsing -m short argument."""
        args = parse_args(["-m", "gaming"])
        assert args.mode == "gaming"

    def test_parse_config_path(self):
        """Test parsing --config argument."""
        args = parse_args(["--config", "/path/to/config.yaml"])
        assert args.config == "/path/to/config.yaml"

    def test_parse_panic_flag(self):
        """Test parsing --panic flag."""
        args = parse_args(["--panic"])
        assert args.panic is True

    def test_parse_quit_flag(self):
        """Test parsing --quit flag."""
        args = parse_args(["--quit"])
        assert args.quit is True

    def test_parse_clear_flag(self):
        """Test parsing --clear flag."""
        args = parse_args(["--clear"])
        assert args.clear is True

    def test_parse_init_flag(self):
        """Test parsing --init flag."""
        args = parse_args(["--init"])
        assert args.init is True

    def test_parse_dev_flag(self):
        """Test parsing --dev flag."""
        args = parse_args(["--dev"])
        assert args.dev is True

    def test_parse_status_flag(self):
        """Test parsing --status flag."""
        args = parse_args(["--status"])
        assert args.status is True

    def test_parse_list_flag(self):
        """Test parsing --list flag."""
        args = parse_args(["--list"])
        assert args.list is True

    def test_parse_kill_flag(self):
        """Test parsing --kill flag."""
        args = parse_args(["--kill"])
        assert args.kill is True

    def test_parse_reload_flag(self):
        """Test parsing --reload flag."""
        args = parse_args(["--reload"])
        assert args.reload is True

    def test_parse_suspend_flag(self):
        """Test parsing --suspend flag."""
        args = parse_args(["--suspend"])
        assert args.suspend is True

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
        assert args.quit is False


class TestValidateArgs:
    """Test argument validation."""

    def test_validate_mode_alone(self):
        """Test valid: mode alone."""
        args = parse_args(["--mode", "work"])
        is_valid, error = validate_args(args)
        assert is_valid is True
        assert error is None

    def test_validate_panic_alone(self):
        """Test valid: panic alone."""
        args = parse_args(["--panic"])
        is_valid, error = validate_args(args)
        assert is_valid is True

    def test_validate_quit_alone(self):
        """Test valid: quit alone."""
        args = parse_args(["--quit"])
        is_valid, error = validate_args(args)
        assert is_valid is True

    def test_validate_clear_alone(self):
        """Test valid: clear alone."""
        args = parse_args(["--clear"])
        is_valid, error = validate_args(args)
        assert is_valid is True

    def test_validate_init_alone(self):
        """Test valid: init alone."""
        args = parse_args(["--init"])
        is_valid, error = validate_args(args)
        assert is_valid is True

    def test_validate_kill_alone(self):
        """Test valid: kill alone."""
        args = parse_args(["--kill"])
        is_valid, error = validate_args(args)
        assert is_valid is True

    def test_validate_suspend_alone(self):
        """Test valid: suspend alone."""
        args = parse_args(["--suspend"])
        is_valid, error = validate_args(args)
        assert is_valid is True

    def test_validate_reload_alone(self):
        """Test valid: reload alone."""
        args = parse_args(["--reload"])
        is_valid, error = validate_args(args)
        assert is_valid is True

    def test_validate_status_alone(self):
        """Test valid: status alone."""
        args = parse_args(["--status"])
        is_valid, error = validate_args(args)
        assert is_valid is True

    def test_validate_list_alone(self):
        """Test valid: list alone."""
        args = parse_args(["--list"])
        is_valid, error = validate_args(args)
        assert is_valid is True

    def test_validate_mode_with_panic(self):
        """Test invalid: mode with panic."""
        args = parse_args(["--mode", "work", "--panic"])
        is_valid, error = validate_args(args)
        assert is_valid is False
        assert "Cannot use --mode with" in error
        assert "--panic" in error

    def test_validate_mode_with_quit(self):
        """Test invalid: mode with quit."""
        args = parse_args(["--mode", "work", "--quit"])
        is_valid, error = validate_args(args)
        assert is_valid is False
        assert "Cannot use --mode with" in error

    def test_validate_mode_with_clear(self):
        """Test invalid: mode with clear."""
        args = parse_args(["--mode", "work", "--clear"])
        is_valid, error = validate_args(args)
        assert is_valid is False
        assert "Cannot use --mode with" in error

    def test_validate_mode_with_kill(self):
        """Test invalid: mode with kill."""
        args = parse_args(["--mode", "work", "--kill"])
        is_valid, error = validate_args(args)
        assert is_valid is False
        assert "Cannot use --mode with" in error

    def test_validate_mode_with_suspend(self):
        """Test invalid: mode with suspend."""
        args = parse_args(["--mode", "work", "--suspend"])
        is_valid, error = validate_args(args)
        assert is_valid is False
        assert "Cannot use --mode with" in error

    def test_validate_panic_and_quit(self):
        """Test invalid: panic and quit together."""
        args = parse_args(["--panic", "--quit"])
        is_valid, error = validate_args(args)
        assert is_valid is False
        assert "Only one action flag allowed" in error

    def test_validate_panic_and_clear(self):
        """Test invalid: panic and clear together."""
        args = parse_args(["--panic", "--clear"])
        is_valid, error = validate_args(args)
        assert is_valid is False

    def test_validate_panic_and_kill(self):
        """Test invalid: panic and kill together."""
        args = parse_args(["--panic", "--kill"])
        is_valid, error = validate_args(args)
        assert is_valid is False

    def test_validate_init_and_reload(self):
        """Test valid: init and reload together (not exclusive)."""
        args = parse_args(["--init", "--reload"])
        is_valid, error = validate_args(args)
        assert is_valid is True

    def test_validate_status_and_list_and_reload(self):
        """Test valid: status, list, and reload together (not exclusive)."""
        args = parse_args(["--status", "--list", "--reload"])
        is_valid, error = validate_args(args)
        assert is_valid is True

    def test_validate_empty_mode(self):
        """Test valid: empty mode name is handled (argparse may reject first)."""
        args = parse_args(["--mode", ""])
        is_valid, error = validate_args(args)
        assert is_valid is True

    def test_validate_whitespace_mode(self):
        """Test invalid: whitespace-only mode name fails validation."""
        args = parse_args(["--mode", "   "])
        is_valid, error = validate_args(args)
        assert is_valid is False
        assert "Mode name cannot be empty" in error


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
        assert "--panic" in msg
