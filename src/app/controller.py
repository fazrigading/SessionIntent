"""
SessionIntent App Controller
Handles launching and reusing applications based on their definitions.
"""

from __future__ import annotations

import asyncio
import subprocess
from typing import Any
from collections.abc import Sequence


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


async def _launch_app_async(cmd: list[str]) -> None:
    """Launch a single app asynchronously."""
    await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
        start_new_session=True,
    )


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
        if not is_running(app_key, dev_mode):
            _print_or_launch([app_key], dev_mode)
        return

    check_pattern = app_def.get("check", app_key)
    if check_pattern is not False and is_running(check_pattern, dev_mode):
        if not app_def.get("internal_reuse", True):
            _print(dev_mode, f"  - {app_key} is already running (skipping)")
            return
        _print(dev_mode, f"  - {app_key} is already running (reusing)")

    _print(dev_mode, f"  - Handling {app_key}...")

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


async def launch_apps_async(
    app_entries: Sequence[str | dict[str, Any]],
    apps: dict[str, dict[str, Any]],
    params: dict[str, Any] | None = None,
    dev_mode: bool = False,
) -> list[tuple[str, bool, str]]:
    """
    Launch multiple apps in parallel asynchronously.

    Args:
        app_entries: List of app entries to launch
        apps: Application registry
        params: Shared parameters for template substitution
        dev_mode: If True, print commands instead of launching

    Returns:
        List of (app_key, success, message) tuples
    """
    params = params or {}
    results: list[tuple[str, bool, str]] = []
    tasks: list[tuple[str, asyncio.Task]] = []

    non_running = _filter_non_running(app_entries, apps, dev_mode)

    if dev_mode:
        for app_key, app_def, local_params in non_running:
            cmd = _build_command(app_def, local_params)
            _print(dev_mode, f"[DEV] Exec: {cmd}")
            results.append((app_key, True, f"[DEV] Exec: {cmd}"))
    else:
        for app_key, app_def, local_params in non_running:
            cmd = _build_command(app_def, local_params)
            task = asyncio.create_task(_launch_app_async(cmd))
            tasks.append((app_key, task))

        done, pending = await asyncio.wait(
            [t for _, t in tasks], return_when=asyncio.ALL_COMPLETED
        )

        for app_key, task in tasks:
            if task in done:
                try:
                    await task
                    results.append((app_key, True, "Launched"))
                except Exception as e:
                    results.append((app_key, False, str(e)))

    return results


def _filter_non_running(
    app_entries: Sequence[str | dict[str, Any]],
    apps: dict[str, dict[str, Any]],
    dev_mode: bool = False,
) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    """Filter apps that are not already running."""
    non_running: list[tuple[str, dict[str, Any], dict[str, Any]]] = []

    for app_entry in app_entries:
        if isinstance(app_entry, str):
            app_key = app_entry
            app_def = apps.get(app_key, {})
            local_params: dict[str, Any] = {}
        else:
            app_key = list(app_entry.keys())[0]
            val = app_entry[app_key]
            app_def = apps.get(app_key, {})
            if isinstance(val, dict):
                local_params = val
            else:
                primary = app_def.get("primary_param", "value")
                local_params = {primary: val}

        if not app_def:
            non_running.append((app_key, {"cmd": [app_key]}, local_params))
            continue

        check_pattern = app_def.get("check", app_key)
        if check_pattern is False or is_running(check_pattern, dev_mode):
            if app_def.get("internal_reuse", True):
                non_running.append((app_key, app_def, local_params))
            continue

        non_running.append((app_key, app_def, local_params))

    return non_running


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
