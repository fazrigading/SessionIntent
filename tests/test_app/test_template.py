"""Tests for app template resolver."""

import pytest

from src.app.template import (
    resolve_template,
    extract_template_vars,
    is_template,
    resolve_if_template,
)


class TestResolveTemplate:
    """Test resolve_template function."""

    def test_resolve_basic(self):
        """Test basic template resolution."""
        assert resolve_template("hello {name}", {"name": "World"}) == "hello World"

    def test_resolve_with_default(self):
        """Test template with default value."""
        assert resolve_template("hello {name|stranger}", {}) == "hello stranger"

    def test_resolve_multiple_vars(self):
        """Test resolving multiple variables."""
        assert (
            resolve_template("{g} {n}", {"g": "Hello", "n": "World"}) == "Hello World"
        )

    def test_resolve_no_params(self):
        """Test resolving with no matching params."""
        assert resolve_template("hello {name}", {}) == "hello "

    def test_resolve_none_value_uses_default(self):
        """Test that None value uses default."""
        assert resolve_template("hi {n|x}", {"n": None}) == "hi x"

    def test_resolve_empty_template(self):
        """Test resolving empty template."""
        assert resolve_template("", {"name": "World"}) == ""

    def test_resolve_no_template_vars(self):
        """Test resolving string without template vars."""
        assert resolve_template("hello world", {"name": "World"}) == "hello world"

    def test_resolve_with_pipe_in_value(self):
        """Test resolving with pipe character in value."""
        assert (
            resolve_template("{cmd}", {"cmd": "echo 'hello|world'"})
            == "echo 'hello|world'"
        )

    def test_resolve_missing_key_uses_default(self):
        """Test missing key uses default value."""
        assert resolve_template("a {b|default} c", {}) == "a default c"


class TestExtractTemplateVars:
    """Test extract_template_vars function."""

    def test_extract_single(self):
        """Test extracting single variable."""
        assert extract_template_vars("hello {name}") == ["name"]

    def test_extract_multiple(self):
        """Test extracting multiple variables."""
        assert extract_template_vars("{a} and {b}") == ["a", "b"]

    def test_extract_no_vars(self):
        """Test extracting with no variables."""
        assert extract_template_vars("hello world") == []

    def test_extract_with_defaults(self):
        """Test extracting variables with defaults."""
        assert extract_template_vars("{a|1} and {b|2}") == ["a", "b"]


class TestIsTemplate:
    """Test is_template function."""

    def test_is_template_true(self):
        """Test is_template returns True for template."""
        assert is_template("{name}") is True

    def test_is_template_false(self):
        """Test is_template returns False for plain text."""
        assert is_template("hello world") is False

    def test_is_template_empty(self):
        """Test is_template with empty string."""
        assert is_template("") is False


class TestResolveIfTemplate:
    """Test resolve_if_template function."""

    def test_resolve_if_template_is_template(self):
        """Test resolve_if_template with template."""
        assert resolve_if_template("hi {n}", {"n": "X"}) == "hi X"

    def test_resolve_if_template_not_template(self):
        """Test resolve_if_template with plain text."""
        assert resolve_if_template("hi world", {"n": "X"}) == "hi world"

    def test_resolve_if_template_non_string(self):
        """Test resolve_if_template with non-string."""
        assert resolve_if_template(42, {"n": "X"}) == 42

    def test_resolve_if_template_dev_mode(self, capsys):
        """Test resolve_if_template in dev mode."""
        result = resolve_if_template("cmd {arg}", {"arg": "val"}, dev_mode=True)
        assert result == "cmd val"
        captured = capsys.readouterr()
        assert "[DEV] Template" in captured.out
