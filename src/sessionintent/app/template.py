"""
SessionIntent App Template Resolver
Resolves template variables in app commands using {variable|default} syntax.
"""

from __future__ import annotations

import re
from typing import Any


def resolve_template(template: str, params: dict[str, Any]) -> str:
    """
    Resolve template variables in a string.

    Format: {variable|default}
    - variable: Key from params dict
    - default: Optional fallback value (after pipe)

    Examples:
        >>> resolve_template("hello {name|world}", {"name": "Alice"})
        'hello Alice'

        >>> resolve_template("hello {name|world}", {})
        'hello world'

        >>> resolve_template("path: {path|/default}", {"path": None})
        'path: /default'

    Args:
        template: String containing template variables
        params: Dictionary of values for substitution

    Returns:
        String with variables replaced

    Raises:
        ValueError: If template syntax is invalid
    """
    if not template:
        return ""

    if not params:
        # No params, just remove defaults
        def remove_default(match):
            parts = match.group(1).split("|", 1)
            return parts[1] if len(parts) > 1 else ""

        return re.sub(r"\{([^}]+)\}", remove_default, template)

    def replace(match):
        parts = match.group(1).split("|", 1)
        key = parts[0]
        default = parts[1] if len(parts) > 1 else ""
        val = params.get(key, default)
        if val is None:
            val = default
        return str(val)

    return re.sub(r"\{([^}]+)\}", replace, template)


def extract_template_vars(template: str) -> list:
    """
    Extract all template variable names from a string.

    Args:
        template: String containing template variables

    Returns:
        List of variable names (without defaults)

    Example:
        >>> extract_template_vars("cmd {a|1} and {b|2}")
        ['a', 'b']
    """
    pattern = r"\{([^}]+)\}"
    matches = re.findall(pattern, template)

    vars_list = []
    for match in matches:
        key = match.split("|")[0]
        vars_list.append(key)

    return vars_list


def is_template(text: str) -> bool:
    """Check if text contains any template variables."""
    return bool(re.search(r"\{([^}]+)\}", text))


def resolve_if_template(
    value: Any, params: dict[str, Any], dev_mode: bool = False
) -> Any:
    """
    Resolve a value as template if it's a string containing templates.

    Args:
        value: Value to potentially resolve
        params: Template parameters
        dev_mode: If True, print what would be resolved

    Returns:
        Resolved value (same type as input if not a template string)
    """
    if not isinstance(value, str) or not is_template(value):
        return value

    resolved = resolve_template(value, params)

    if dev_mode:
        print(f"[DEV] Template: {value} -> {resolved}")

    return resolved
