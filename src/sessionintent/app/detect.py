"""
SessionIntent App Detection
Detects installed applications from multiple sources.
"""

from __future__ import annotations

import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml


def load_app_categories() -> dict[str, list[str]]:
    """Load app categories from YAML file."""
    yaml_path = Path(__file__).parent / "app_categories.yaml"
    if yaml_path.exists():
        try:
            with open(yaml_path, "r") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError:
            pass
    return {}


APP_CATEGORIES: dict[str, list[str]] = load_app_categories()


def detect_flatpak_apps() -> dict[str, dict[str, Any]]:
    """Detect apps installed via Flatpak."""
    apps: dict[str, dict[str, Any]] = {}

    try:
        result = subprocess.run(
            ["flatpak", "list", "--app", "--columns=application"],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            app_id = line.strip()
            name = app_id.split(".")[-1].replace("-", "_")
            apps[name] = {
                "cmd": ["flatpak", "run", app_id],
                "check": name,
                "internal_reuse": False,
            }
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return apps


def _split_exec(exec_line: str) -> list[str]:
    """Split an Exec line on shell quoting, dropping freedesktop field codes."""
    try:
        parts = shlex.split(exec_line, posix=True)
    except ValueError:
        parts = exec_line.split()
    # ponytail: field codes are exactly 2 chars (%f, %U, ...); keep real flags
    return [p for p in parts if not (p.startswith("%") and len(p) == 2)]


def _parse_desktop_entry(content: str) -> dict[str, str]:
    """Extract fields from the [Desktop Entry] section only."""
    fields: dict[str, str] = {}
    in_entry = False
    for raw_line in content.split("\n"):
        line = raw_line.strip()
        if line.startswith("[") and line.endswith("]"):
            in_entry = line == "[Desktop Entry]"
            continue
        if not in_entry or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key in (
            "Name",
            "Exec",
            "StartupWMClass",
            "StartupNotify",
            "NoDisplay",
            "Hidden",
            "Type",
        ):
            fields[key] = value.strip()
    return fields


def detect_desktop_apps(
    desktop_dirs: list[Path] | None = None,
) -> dict[str, dict[str, Any]]:
    """Detect apps from .desktop files."""
    apps: dict[str, dict[str, Any]] = {}

    if desktop_dirs is None:
        desktop_dirs = [
            Path("/usr/share/applications"),
            Path("/usr/local/share/applications"),
            Path.home() / ".local/share/applications",
        ]

    for desktop_dir in desktop_dirs:
        if not desktop_dir.exists():
            continue

        for desktop_file in desktop_dir.glob("*.desktop"):
            try:
                content = desktop_file.read_text()
            except OSError:
                continue

            entry = _parse_desktop_entry(content)
            if entry.get("Type", "Application") != "Application":
                continue
            if entry.get("NoDisplay", "false").lower() == "true":
                continue
            if entry.get("Hidden", "false").lower() == "true":
                continue

            exec_line = entry.get("Exec", "")
            name = entry.get("Name", "")
            if not exec_line or not name:
                continue

            cmd = _split_exec(exec_line)
            if not cmd:
                continue

            key = name.lower().replace(" ", "-").replace("_", "-")
            for char in key:
                if char in "[](){}":
                    key = key.replace(char, "")

            if key in apps:
                continue

            binary = cmd[0].split("/")[-1]
            apps[key] = {
                "cmd": cmd,
                "check": binary,
                "internal_reuse": entry.get("StartupNotify", "true").lower()
                == "true",
                "wm_class": entry.get("StartupWMClass", "") or binary,
                "desktop_id": desktop_file.stem,
            }

    return apps


def detect_dpkg_apps() -> dict[str, dict[str, Any]]:
    """Detect apps installed via dpkg (Debian/Ubuntu)."""
    apps: dict[str, dict[str, Any]] = {}

    try:
        result = subprocess.run(
            ["dpkg", "-l"],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.strip().split("\n"):
            if not line.startswith("ii "):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            pkg_name = parts[1].split(":")[0]  # strip arch suffix (foo:amd64)
            if " " in pkg_name:
                continue

            exec_name = pkg_name
            if shutil.which(exec_name) is None:
                continue

            key = exec_name.lower().replace("_", "-")
            if key in apps:
                continue

            apps[key] = {
                "cmd": [exec_name],
                "check": exec_name,
                "internal_reuse": False,
            }
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return apps


def detect_rpm_apps() -> dict[str, dict[str, Any]]:
    """Detect apps installed via rpm (Fedora/RHEL)."""
    apps: dict[str, dict[str, Any]] = {}

    try:
        result = subprocess.run(
            ["rpm", "-qa", "--queryformat", "%{NAME}\\n"],
            capture_output=True,
            text=True,
            check=True,
        )
        for pkg_name in result.stdout.strip().split("\n"):
            if not pkg_name:
                continue

            exec_name = pkg_name
            if shutil.which(exec_name) is None:
                continue

            key = exec_name.lower().replace("_", "-")
            if key in apps:
                continue

            apps[key] = {
                "cmd": [exec_name],
                "check": exec_name,
                "internal_reuse": False,
            }
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return apps


def categorize_app(app_key: str) -> str:
    """Categorize an app based on its name."""
    app_key_lower = app_key.lower()

    for category, keywords in APP_CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in app_key_lower:
                return category

    return "Other"


def detect_all_apps(use_cache: bool = True) -> dict[str, dict[str, Any]]:
    """
    Detect all installed applications from all sources.
    Priority: flatpak > desktop > dpkg > rpm

    Args:
        use_cache: If True, use cached results if valid. Defaults to True.

    Returns:
        Dictionary of detected applications.
    """
    from .cache import get_cached_apps, is_cache_valid, save_app_cache

    if use_cache and is_cache_valid():
        cached = get_cached_apps()
        if cached:
            return cached

    detected: dict[str, dict[str, Any]] = {}

    sources = [
        ("flatpak", detect_flatpak_apps()),
        ("desktop", detect_desktop_apps()),
        ("dpkg", detect_dpkg_apps()),
        ("rpm", detect_rpm_apps()),
    ]

    for source_name, source_apps in sources:
        for app_key, app_data in source_apps.items():
            if app_key not in detected:
                detected[app_key] = app_data.copy()
                detected[app_key]["_source"] = source_name
                detected[app_key]["_category"] = categorize_app(app_key)

    if use_cache:
        save_app_cache(detected)

    return detected


def get_categorized_apps(
    apps: dict[str, dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:
    """Group apps by category."""
    categorized: dict[str, dict[str, dict[str, Any]]] = {}

    for app_key, app_data in apps.items():
        category = app_data.get("_category", "Other")
        if category not in categorized:
            categorized[category] = {}
        app_copy = {k: v for k, v in app_data.items() if not k.startswith("_")}
        categorized[category][app_key] = app_copy

    return categorized


def get_category_list() -> list[tuple[str, int]]:
    """Return list of categories with numbers."""
    categories = [
        "Browsers",
        "Development",
        "Media Players",
        "Art Editing",
        "Communication",
        "Games",
        "Productivity",
        "Utilities",
        "System",
        "Other",
    ]
    return [(cat, i + 1) for i, cat in enumerate(categories)]