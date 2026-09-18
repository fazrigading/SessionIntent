"""
SessionIntent Setup
Interactive setup wizard for first-run and app scanning.
"""

from __future__ import annotations

from typing import Any

from ..app.detect import (
    detect_all_apps,
    get_category_list,
    get_categorized_apps,
)
from ..constants import APPS_PATH, CONFIG_DIR, CONFIG_PATH, DEFAULT_CONFIG
from ..session.log import info


CATEGORY_HEADER = {
    "Browsers": "# Browsers",
    "Development": "# Development",
    "Media Players": "# Media Players",
    "Art Editing": "# Art Editing",
    "Communication": "# Communication",
    "Games": "# Games",
    "Productivity": "# Productivity",
    "Utilities": "# Utilities",
    "System": "# System",
    "Other": "# Other",
}


def prompt_yes_no(prompt_text: str) -> bool:
    """Prompt user for yes/no input."""
    while True:
        try:
            response = input(f"{prompt_text} [Y/n]: ").strip().lower()
            if response in ("y", "yes", ""):
                return True
            if response in ("n", "no"):
                return False
        except (KeyboardInterrupt, EOFError):
            return False


def prompt_numbered_list(prompt_text: str, items: list[str]) -> list[int]:
    """Prompt user to select numbered items."""
    while True:
        try:
            print(prompt_text)
            response = input("Enter numbers (comma-separated): ").strip()
            if not response:
                return []

            selected = []
            for part in response.split(","):
                part = part.strip()
                if not part.isdigit():
                    continue
                num = int(part)
                if 1 <= num <= len(items):
                    selected.append(num)

            return selected
        except (KeyboardInterrupt, EOFError):
            return []


def parse_selection(selection_str: str, max_num: int) -> list[int]:
    """Parse comma-separated selection string."""
    selected = []
    for part in selection_str.split(","):
        part = part.strip()
        if not part.isdigit():
            continue
        num = int(part)
        if 1 <= num <= max_num:
            selected.append(num)
    return selected


def select_categories(categorized: dict[str, dict[str, dict[str, Any]]]) -> list[str]:
    """Prompt user to select categories."""
    categories = get_category_list()
    print("\nSelect categories to include:")
    for cat, num in categories:
        count = len(categorized.get(cat, {}))
        print(f"  {num}. {cat} ({count} apps)")
    all_count = sum(len(apps) for apps in categorized.values())
    print(f"  11. All categories ({all_count} apps)")

    while True:
        try:
            response = input("\nEnter numbers (comma-separated): ").strip()
            if not response:
                return []

            numbers = parse_selection(response, 11)
            if 11 in numbers:
                return [cat for cat, _ in categories]
            if 11 not in numbers and numbers:
                selected = []
                for num in numbers:
                    if 1 <= num <= 10:
                        selected.append(categories[num - 1][0])
                return selected
        except (KeyboardInterrupt, EOFError):
            return []


def select_apps_option() -> int:
    """Prompt user to select app inclusion option."""
    print("\nSelect apps to include:")
    print("  1. Exclude few apps (include all, then exclude selected)")
    print("  2. Include few apps (start fresh, include only selected)")
    print("  3. Use all apps")

    while True:
        try:
            response = input("\nEnter number: ").strip()
            if response.isdigit() and 1 <= int(response) <= 3:
                return int(response)
        except (KeyboardInterrupt, EOFError):
            return 3


def select_apps_to_exclude(categorized_apps: dict[str, dict[str, Any]]) -> set[str]:
    """Prompt user to select apps to exclude."""
    excluded: set[str] = set()

    for category, apps in categorized_apps.items():
        print(f"\n{category}:")
        app_list = list(apps.keys())
        for i, app_key in enumerate(app_list, 1):
            print(f"  {i}. {app_key}")

        if not app_list:
            continue

        try:
            response = input(
                "Enter numbers to EXCLUDE (comma-separated, or press Enter to skip): "
            ).strip()
            if not response:
                continue

            numbers = parse_selection(response, len(app_list))
            for num in numbers:
                excluded.add(app_list[num - 1])
        except (KeyboardInterrupt, EOFError):
            pass

    return excluded


def select_apps_to_include(categorized_apps: dict[str, dict[str, Any]]) -> set[str]:
    """Prompt user to select apps to include."""
    included: set[str] = set()

    for category, apps in categorized_apps.items():
        print(f"\n{category}:")
        app_list = list(apps.keys())
        for i, app_key in enumerate(app_list, 1):
            print(f"  {i}. {app_key}")

        if not app_list:
            continue

        try:
            response = input(
                "Enter numbers to INCLUDE (comma-separated, or press Enter for all): "
            ).strip()
            if not response:
                included.update(app_list)
                continue

            numbers = parse_selection(response, len(app_list))
            for num in numbers:
                included.add(app_list[num - 1])
        except (KeyboardInterrupt, EOFError):
            pass

    return included


def build_apps_yaml(
    apps: dict[str, dict[str, Any]],
    selected_categories: list[str],
) -> str:
    """Build YAML content for apps.yaml."""
    from ..app.detect import APP_CATEGORIES

    categorized: dict[str, dict[str, dict[str, Any]]] = {}

    for app_key, app_data in apps.items():
        found_category = None
        app_key_lower = app_key.lower()

        for cat in selected_categories:
            if cat in APP_CATEGORIES:
                for kw in APP_CATEGORIES[cat]:
                    if kw.lower() in app_key_lower:
                        found_category = cat
                        break
            if found_category:
                break

        if not found_category:
            found_category = "Other"

        if found_category not in categorized:
            categorized[found_category] = {}
        categorized[found_category][app_key] = app_data

    lines = [
        "# SessionIntent Apps Configuration",
        "#",
        "# Customize launch parameters:",
        "#   - {profile|default} → Firefox profile name",
        "#   - {workspace|} → VSCode workspace path",
        "#   - append_param for URLs to open",
        "#   - primary_param for workspace/project path",
        "#   - flags for CLI options (background, etc.)",
        "#",
        "# Reference: https://github.com/fazrigading/sessionintent",
        "#",
        "",
    ]

    for category in selected_categories:
        if category in CATEGORY_HEADER:
            lines.append(CATEGORY_HEADER[category])

        if category in categorized:
            for app_key, app_data in sorted(categorized[category].items()):
                lines.append(f"{app_key}:")
                if cmd := app_data.get("cmd"):
                    lines.append(f"  cmd: {cmd}")
                if check := app_data.get("check"):
                    if check is False:
                        lines.append("  check: false")
                    else:
                        lines.append(f"  check: {check!r}")
                if internal := app_data.get("internal_reuse"):
                    lines.append(f"  internal_reuse: {internal}")
                lines.append("")

    return "\n".join(lines)


def write_apps_yaml(content: str) -> None:
    """Write apps.yaml to user config directory."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(APPS_PATH, "w") as f:
        f.write(content)
    info(f"Apps configuration written to {APPS_PATH}")


def write_config_yaml() -> None:
    """Write default config.yaml to user config directory."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        f.write(DEFAULT_CONFIG)
    info(f"Default config written to {CONFIG_PATH}")


def setup_interactive(add_new_only: bool = False, use_cache: bool = True) -> None:
    """
    Run interactive setup wizard.

    Args:
        add_new_only: If True, only add new detected apps.
        use_cache: If True, use cached detection results. Defaults to True.
    """
    if not CONFIG_PATH.exists():
        write_config_yaml()

    print("Scanning for installed applications...")

    detected = detect_all_apps(use_cache=use_cache)
    if not detected:
        print("No applications detected on this system.")
        use_example = prompt_yes_no(
            "Would you like to use example apps from GitHub repo"
        )
        if use_example:
            print(
                "Run: curl -o ~/.config/sessionintent/apps.yaml "
                "https://raw.githubusercontent.com/fazrigading/sessionintent/"
                "main/examples/apps.example.yaml"
            )
        return

    categories = get_category_list()
    print(f"\nFound {len(detected)} applications in {len(categories) + 1} categories.")

    categorized = get_categorized_apps(detected)
    selected_categories = select_categories(categorized)
    if not selected_categories:
        print("No categories selected. Aborting.")
        return

    filtered = {
        cat: apps
        for cat, apps in categorized.items()
        if cat in selected_categories
    }
    
    option = select_apps_option()

    final_apps: dict[str, dict[str, Any]] = {}

    if option == 1:
        all_flat = {}
        for cat_apps in filtered.values():
            all_flat.update(cat_apps)
        excluded = select_apps_to_exclude(filtered)
        final_apps = {k: v for k, v in all_flat.items() if k not in excluded}
    elif option == 2:
        included = select_apps_to_include(filtered)
        for cat_apps in filtered.values():
            for app_key, app_data in cat_apps.items():
                if app_key in included:
                    final_apps[app_key] = app_data
    else:
        for cat_apps in filtered.values():
            final_apps.update(cat_apps)

    if not final_apps:
        print("No apps selected. Aborting.")
        return

    yaml_content = build_apps_yaml(final_apps, selected_categories)
    write_apps_yaml(yaml_content)

    print(f"\nSetup complete! {len(final_apps)} apps configured.")


def rescan_options(use_cache: bool = True) -> None:
    """
    Offer rescan options and run selected.

    Args:
        use_cache: If True, use cached detection results. Defaults to True.
    """
    print("\nRescan options:")
    print("  1. Rescan all apps (re-do entire selection)")
    print("  2. Add only new detected apps")

    while True:
        try:
            response = input("\nEnter number: ").strip()
            if response.isdigit() and 1 <= int(response) <= 2:
                option = int(response)
                break
        except (KeyboardInterrupt, EOFError):
            return

    if option == 1:
        setup_interactive(add_new_only=False, use_cache=use_cache)
    else:
        setup_interactive(add_new_only=True, use_cache=use_cache)