"""Tests for the subcommand CLI parser."""

import argparse

import pytest

from sessionintent.cli.parser import (
    COMMANDS,
    create_parser,
    get_help_message,
    parse_args,
)


class TestCreateParser:
    def test_parser_creation(self):
        assert create_parser() is not None

    def test_all_commands_registered(self):
        parser = create_parser()
        sub = next(
            action
            for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        )
        assert set(sub.choices) == set(COMMANDS)


class TestParseCommands:
    @pytest.mark.parametrize("command", list(COMMANDS))
    def test_each_command_parses(self, command):
        argv = [command] if command != "apply" else [command, "work"]
        args = parse_args(argv)
        assert args.command == command

    def test_apply_takes_mode(self):
        assert parse_args(["apply", "work"]).mode == "work"

    def test_no_command_defaults_to_none(self):
        assert parse_args([]).command is None

    def test_global_flags(self):
        args = parse_args(["--dev", "--config", "c.yaml", "status"])
        assert args.dev is True
        assert args.config == "c.yaml"
        assert args.command == "status"

    def test_scan_flags(self):
        args = parse_args(["scan", "--force", "--no-cache"])
        assert args.force is True
        assert args.no_cache is True

    def test_backend_choices(self):
        assert parse_args(["--backend", "sway"]).backend == "sway"
        with pytest.raises(SystemExit):
            parse_args(["--backend", "bspwm"])


class TestGetHelpMessage:
    def test_help_lists_commands(self):
        msg = get_help_message()
        assert isinstance(msg, str)
        assert "apply" in msg
        assert "select" in msg
