"""
SessionIntent App Controller
Handles launching and reusing applications based on their definitions.
"""

from __future__ import annotations

import subprocess
from typing import Any


def is_running(pattern: str, dev_mode: bool = False) -> bool:
    """
    Check if a process matching pattern is running.

    Args:
        pattern: Pattern to search for (passed to pgrep -f)
        dev_mode: If True, always returns False (no processes running)

    Returns:
        True if process is running, False otherwise
    """
    if dev_mode:
        return False

    try:
        subprocess.run(["pgrep", "-f", pattern], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def launch_app(
    app_key: str,
    params: dict[str, Any],
    apps: dict[str, dict[str, Any]],
    dev_mode: bool = False,
) -> None:
    """
    Launch or reuse an application based on its definition.

    Args:
        app_key: The app identifier (e.g., 'firefox', 'vscode')
        params: Parameters for template substitution and flags
        apps: Application registry with definitions
        dev_mode: If True, print commands instead of launching
    """
    app_def = apps.get(app_key, {})

    if not app_def:
        # Generic app launch (not in registry)
        if not is_running(app_key, dev_mode):
            _print_or_launch([app_key], dev_mode)
        return

    # Check if app is already running
    check_pattern = app_def.get("check", app_key)
    if check_pattern is not False and is_running(check_pattern, dev_mode):
        if not app_def.get("internal_reuse", True):
            _print(dev_mode, f"  - {app_key} is already running (skipping)")
            return
        _print(dev_mode, f"  - {app_key} is already running (reusing)")

    _print(dev_mode, f"  - Handling {app_key}...")

    # Build command
    cmd = _build_command(app_def, params)

    if dev_mode:
        _print(dev_mode, f"[DEV] Exec: {cmd}")
    else:
        subprocess.Popen(
            cmd,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _build_command(app_def: dict[str, Any], params: dict[str, Any]) -> list[str]:
    """Build the complete command list from app definition and parameters."""
    cmd = []
    raw_cmd = app_def.get("cmd", [])

    # Resolve templates in command parts
    for part in raw_cmd:
        if "{" in part and "}" in part:
            resolved = resolve_template(part, params)
            if resolved:
                cmd.append(resolved)
        else:
            cmd.append(part)

    # Add flags based on parameters
    flags = app_def.get("flags", {})
    for p_key, flag_val in flags.items():
        if params.get(p_key):
            cmd.append(flag_val)

    # Append param values (e.g., list of URLs)
    ap = app_def.get("append_param")
    if ap and ap in params:
        vals = params[ap]
        if isinstance(vals, list):
            cmd.extend(vals)
        else:
            cmd.append(vals)

    return cmd


def resolve_template(template: str, params: dict[str, Any]) -> str:
    """
    Resolve template variables in a string.

    Format: {variable|default}
    - variable: Key from params dict
    - default: Optional fallback value

    Args:
        template: String with template variables
        params: Dictionary of values for substitution

    Returns:
        String with variables replaced, or empty string if resolution fails
    """
    import re

    def replace(match):
        parts = match.group(1).split("|", 1)
        key = parts[0]
        default = parts[1] if len(parts) > 1 else ""
        val = params.get(key, default)
        if val is None:
            val = default
        return str(val)

    return re.sub(r"\{([^}]+)\}", replace, template)


def _print(dev_mode: bool, message: str) -> None:
    """Print message if not in dev mode, otherwise print with [DEV] prefix."""
    if dev_mode:
        print(message)


def _print_or_launch(cmd: list[str], dev_mode: bool) -> None:
    """Print or launch command based on dev mode."""
    if dev_mode:
        print(f"[DEV] Exec: {cmd}")
    else:
        subprocess.Popen(
            cmd,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
