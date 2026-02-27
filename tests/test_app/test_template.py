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


class TestIsTemplate:
    """Test is_template function."""

    def test_is_template_true(self):
        """Test is_template returns True for template."""
        assert is_template("{name}") is True

    def test_is_template_false(self):
        """Test is_template returns False for plain text."""
        assert is_template("hello world") is False


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
