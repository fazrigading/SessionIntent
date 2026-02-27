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

    def test_resolve_simple_variable(self):
        """Test resolving a simple variable."""
        template = "hello {name}"
        params = {"name": "World"}
        result = resolve_template(template, params)
        assert result == "hello World"

    def test_resolve_with_default(self):
        """Test resolving with default value."""
        template = "hello {name|stranger}"
        params = {}
        result = resolve_template(template, params)
        assert result == "hello stranger"

    def test_resolve_with_default_provided(self):
        """Test resolving with default when value exists."""
        template = "hello {name|stranger}"
        params = {"name": "Alice"}
        result = resolve_template(template, params)
        assert result == "hello Alice"

    def test_resolve_multiple_variables(self):
        """Test resolving multiple variables."""
        template = "{greeting} {name}, you have {count} messages"
        params = {"greeting": "Hello", "name": "Alice", "count": 5}
        result = resolve_template(template, params)
        assert result == "Hello Alice, you have 5 messages"

    def test_resolve_multiple_same_variable(self):
        """Test resolving same variable multiple times."""
        template = "{name} said hi to {name}"
        params = {"name": "Alice"}
        result = resolve_template(template, params)
        assert result == "Alice said hi to Alice"

    def test_resolve_no_params(self):
        """Test resolving with empty params removes defaults."""
        template = "hello {name|world}"
        params = {}
        result = resolve_template(template, params)
        assert result == "hello world"

    def test_resolve_empty_template(self):
        """Test resolving empty template."""
        template = ""
        params = {"name": "World"}
        result = resolve_template(template, params)
        assert result == ""

    def test_resolve_empty_params(self):
        """Test resolving with empty params dict."""
        template = "hello {name}"
        params = {}
        result = resolve_template(template, params)
        assert result == "hello "

    def test_resolve_none_value_uses_default(self):
        """Test that None value uses default."""
        template = "hello {name|stranger}"
        params = {"name": None}
        result = resolve_template(template, params)
        assert result == "hello stranger"

    def test_resolve_missing_key_uses_default(self):
        """Test that missing key uses default."""
        template = "hello {name|stranger}"
        params = {"other": "value"}
        result = resolve_template(template, params)
        assert result == "hello stranger"

    def test_resolve_empty_string_value(self):
        """Test that empty string value is used (not default)."""
        template = "hello {name|stranger}"
        params = {"name": ""}
        result = resolve_template(template, params)
        assert result == "hello "

    def test_resolve_only_defaults(self):
        """Test template with only default values."""
        template = "{a|1} and {b|2}"
        params = {}
        result = resolve_template(template, params)
        assert result == "1 and 2"

    def test_resolve_no_variables_returns_original(self):
        """Test template without variables returns original."""
        template = "hello world"
        params = {"name": "World"}
        result = resolve_template(template, params)
        assert result == "hello world"

    def test_resolve_variable_with_empty_default(self):
        """Test variable with empty default."""
        template = "hello {name|}"
        params = {}
        result = resolve_template(template, params)
        assert result == "hello "

    def test_resolve_preserves_non_template_text(self):
        """Test that non-template text is preserved."""
        template = "cmd {app} --flag {value|default}"
        params = {"app": "firefox", "value": "test"}
        result = resolve_template(template, params)
        assert result == "cmd firefox --flag test"

    def test_resolve_integer_values(self):
        """Test resolving integer values."""
        template = "count: {count}"
        params = {"count": 42}
        result = resolve_template(template, params)
        assert result == "count: 42"

    def test_resolve_boolean_values(self):
        """Test resolving boolean values."""
        template = "enabled: {enabled}"
        params = {"enabled": True}
        result = resolve_template(template, params)
        assert result == "enabled: True"

    def test_resolve_list_value(self):
        """Test resolving list value (converted to string)."""
        template = "values: {items}"
        params = {"items": ["a", "b"]}
        result = resolve_template(template, params)
        assert result == "values: ['a', 'b']"

    def test_resolve_mixed_defaults(self):
        """Test template with mixed variables (some with defaults, some without)."""
        template = "{first} and {second|default}"
        params = {"first": "1"}
        result = resolve_template(template, params)
        assert result == "1 and default"


class TestExtractTemplateVars:
    """Test extract_template_vars function."""

    def test_extract_single_variable(self):
        """Test extracting single variable."""
        template = "hello {name}"
        result = extract_template_vars(template)
        assert result == ["name"]

    def test_extract_multiple_variables(self):
        """Test extracting multiple variables."""
        template = "{a} and {b} and {c}"
        result = extract_template_vars(template)
        assert result == ["a", "b", "c"]

    def test_extract_with_defaults(self):
        """Test extracting variables with defaults."""
        template = "{name|default} and {count|0}"
        result = extract_template_vars(template)
        assert result == ["name", "count"]

    def test_extract_no_variables(self):
        """Test extracting from string without variables."""
        template = "hello world"
        result = extract_template_vars(template)
        assert result == []

    def test_extract_empty_template(self):
        """Test extracting from empty template."""
        template = ""
        result = extract_template_vars(template)
        assert result == []

    def test_extract_complex_template(self):
        """Test extracting from complex template."""
        template = "cmd {app} -p {port|8080} --flag {verbose}"
        result = extract_template_vars(template)
        assert result == ["app", "port", "verbose"]

    def test_extract_duplicate_variables(self):
        """Test extracting duplicate variables."""
        template = "{name} said {name}"
        result = extract_template_vars(template)
        assert result == ["name", "name"]


class TestIsTemplate:
    """Test is_template function."""

    def test_is_template_true_simple(self):
        """Test is_template returns True for simple template."""
        assert is_template("{name}") is True

    def test_is_template_true_with_default(self):
        """Test is_template returns True for template with default."""
        assert is_template("{name|default}") is True

    def test_is_template_true_multiple(self):
        """Test is_template returns True for multiple templates."""
        assert is_template("{a} and {b}") is True

    def test_is_template_false_plain_text(self):
        """Test is_template returns False for plain text."""
        assert is_template("hello world") is False

    def test_is_template_false_empty(self):
        """Test is_template returns False for empty string."""
        assert is_template("") is False

    def test_is_template_false_single_brace(self):
        """Test is_template returns False for single brace (not a template)."""
        assert is_template("hello { world") is False
        assert is_template("hello } world") is False


class TestResolveIfTemplate:
    """Test resolve_if_template function."""

    def test_resolve_if_template_is_template(self):
        """Test resolving when value is a template."""
        value = "hello {name}"
        params = {"name": "World"}
        result = resolve_if_template(value, params)
        assert result == "hello World"

    def test_resolve_if_template_not_template(self):
        """Test returns original value when not a template."""
        value = "hello world"
        params = {"name": "World"}
        result = resolve_if_template(value, params)
        assert result == "hello world"

    def test_resolve_if_template_non_string(self):
        """Test returns original value when not a string."""
        value = 42
        params = {"name": "World"}
        result = resolve_if_template(value, params)
        assert result == 42

    def test_resolve_if_template_list(self):
        """Test returns original value when it's a list."""
        value = ["hello", "{name}"]
        params = {"name": "World"}
        result = resolve_if_template(value, params)
        assert result == ["hello", "{name}"]

    def test_resolve_if_template_dev_mode(self, capsys):
        """Test resolve_if_template in dev mode prints message."""
        value = "hello {name}"
        params = {"name": "World"}
        result = resolve_if_template(value, params, dev_mode=True)
        assert result == "hello World"
        captured = capsys.readouterr()
        assert "Template:" in captured.out
        assert "hello {name}" in captured.out
        assert "hello World" in captured.out
